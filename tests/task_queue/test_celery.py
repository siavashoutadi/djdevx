"""Tests for Celery task-queue management."""

import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.core.process import PixiRunner
from djdevx.main import app
from djdevx.utils.tracking import ProjectTracking, Section
from tests.test_helpers import create_test_django_project

runner = CliRunner()


def _assert_celery_app_exists(root: Path) -> None:
    celery_file = root / "applications" / "celery.py"
    assert celery_file.exists(), "applications/celery.py missing"
    content = celery_file.read_text()
    assert 'app = Celery("test_django_project")' in content, (
        "celery app must render the project name"
    )
    assert (
        'app.config_from_object("django.conf:settings", namespace="CELERY")' in content
    )
    assert "app.autodiscover_tasks()" in content
    assert "from otel.setup import setup_otel" in content, (
        "applications/celery.py must hook otel setup for worker/beat instrumentation"
    )
    assert "except ImportError:" in content, "otel hook must be optional"
    # The app lives under the ``applications`` package so it never shadows the
    # installed ``celery`` package with a root-level ``celery.py`` module.
    assert not (root / "celery.py").exists(), (
        "root celery.py would shadow the celery package (breaks -A and otel)"
    )

    tasks_file = root / "tasks.py"
    assert tasks_file.exists(), "tasks.py missing"
    assert "@shared_task" in tasks_file.read_text()

    settings_file = root / "settings" / "django" / "celery.py"
    assert settings_file.exists(), "settings/django/celery.py missing"
    content = settings_file.read_text()
    assert "class CelerySettings(AppBaseSettings):" in content
    assert "redis_port: int = 6379" in content
    assert "CELERY_BROKER_URL" in content
    assert "CELERY_RESULT_BACKEND" in content
    # Broker/result URLs must embed the redis password: the dev Redis service
    # and the ``cache`` compose service both require ``redis_password``, and a
    # passwordless URL fails every connection with an auth error.
    assert "redis_password" in content
    assert "redis://:redis_password@cache:6379/0" in content, (
        "devcontainer override must point at the password-protected cache compose service"
    )
    assert "redis://:redis_password@cache:6379/1" in content
    assert "quote(" in content, "broker URL must URL-encode the embedded password"


def _assert_celery_app_absent(root: Path) -> None:
    assert not (root / "applications" / "celery.py").exists(), (
        "applications/celery.py should be removed"
    )
    assert not (root / "tasks.py").exists(), "tasks.py should be removed"
    assert not (root / "settings" / "django" / "celery.py").exists(), (
        "settings/django/celery.py should be removed"
    )


def _assert_worker_compose_service(root: Path) -> None:
    compose_file = root / ".devcontainer" / "docker-compose.yaml"
    assert compose_file.exists(), "docker-compose.yaml missing"
    content = compose_file.read_text()
    assert "celery-worker:" in content, "celery-worker service missing"
    # YAML may fold the long command scalar across lines — compare whitespace-flattened.
    flat = " ".join(content.split())
    assert "pixi run celery -A applications.celery worker --loglevel=info" in flat, (
        "celery worker command missing"
    )
    assert "celery-beat:" not in content, "beat must not exist without scheduler"


def test_celery_install_and_remove(temp_dir):
    """Celery task-queue install (auto-installs redis) and remove."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["task-queue", "add", "celery"])
    assert result.exit_code == 0, f"Celery install failed: {result.output}"
    assert "Celery installed." in result.stdout

    # needs: Redis cache auto-installed as the broker.
    assert ProjectTracking().is_installed(Section.CACHE, "redis"), (
        "redis cache not auto-installed as the celery broker"
    )
    assert PixiRunner().has_dependency("django-redis"), (
        "django-redis not installed alongside celery"
    )
    assert PixiRunner().has_dependency("celery"), (
        "celery dependency not found after installation"
    )
    assert ProjectTracking().is_installed(Section.TASK_QUEUE, "celery"), (
        "celery not tracked after install"
    )

    _assert_celery_app_exists(temp_dir)
    _assert_worker_compose_service(temp_dir)

    # Remove.
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "celery"
        result = runner.invoke(app, ["task-queue", "remove"])
    assert result.exit_code == 0, f"Celery remove failed: {result.output}"
    assert "Celery removed." in result.stdout

    assert not PixiRunner().has_dependency("celery"), (
        "celery dependency still present after removal"
    )
    _assert_celery_app_absent(temp_dir)
    compose_content = (temp_dir / ".devcontainer" / "docker-compose.yaml").read_text()
    assert "celery-worker:" not in compose_content, (
        "celery-worker service still in docker-compose after removal"
    )
    # The broker cache is a dependency, not owned by celery — it must remain.
    assert ProjectTracking().is_installed(Section.CACHE, "redis"), (
        "redis cache should not be removed with celery"
    )
    assert not ProjectTracking().is_installed(Section.TASK_QUEUE, "celery"), (
        "celery still tracked after removal"
    )
