"""Tests for Celery Beat scheduler management."""

import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.core.process import PixiRunner
from djdevx.main import app
from djdevx.utils.tracking import ProjectTracking, Section
from tests.test_helpers import create_test_django_project

runner = CliRunner()


def _assert_beat_app_exists(root: Path) -> None:
    settings_file = root / "settings" / "django" / "celery_beat.py"
    assert settings_file.exists(), "settings/django/celery_beat.py missing"
    assert (
        'CELERY_BEAT_SCHEDULER: str = "django_celery_beat.schedulers:DatabaseScheduler"'
        in settings_file.read_text()
    ), "beat must use the database scheduler"

    apps_file = root / "settings" / "apps" / "celery.py"
    assert apps_file.exists(), "settings/apps/celery.py missing"
    assert "django_celery_beat" in apps_file.read_text(), (
        "django_celery_beat not added to INSTALLED_APPS"
    )
    assert "INSTALLED_APPS" in apps_file.read_text()


def _assert_beat_app_absent(root: Path) -> None:
    assert not (root / "settings" / "django" / "celery_beat.py").exists(), (
        "settings/django/celery_beat.py should be removed"
    )
    assert not (root / "settings" / "apps" / "celery.py").exists(), (
        "settings/apps/celery.py should be removed"
    )


def _assert_beat_compose_service(root: Path) -> None:
    compose_file = root / ".devcontainer" / "docker-compose.yaml"
    assert compose_file.exists(), "docker-compose.yaml missing"
    content = compose_file.read_text()
    assert "celery-beat:" in content, "celery-beat service missing"
    # YAML may fold the long command scalar across lines — compare whitespace-flattened.
    flat = " ".join(content.split())
    assert "pixi run celery -A applications.celery beat --loglevel=info" in flat, (
        "celery beat command missing"
    )


def test_celery_beat_install_and_remove(temp_dir):
    """Celery Beat scheduler install (auto-installs the celery worker) and remove."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["scheduler", "add", "celery-beat"])
    assert result.exit_code == 0, f"Scheduler install failed: {result.output}"
    assert "Celery Beat installed." in result.stdout

    # needs: the Celery task-queue is auto-installed.
    assert ProjectTracking().is_installed(Section.TASK_QUEUE, "celery"), (
        "celery task-queue not auto-installed by the scheduler"
    )
    assert PixiRunner().has_dependency("celery"), "celery dependency missing for beat"
    assert PixiRunner().has_dependency("django-celery-beat"), (
        "django-celery-beat not installed"
    )
    assert ProjectTracking().is_installed(Section.SCHEDULER, "celery-beat"), (
        "celery-beat not tracked after install"
    )

    _assert_beat_app_exists(temp_dir)
    _assert_beat_compose_service(temp_dir)

    # Remove.
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "celery-beat"
        result = runner.invoke(app, ["scheduler", "remove"])
    assert result.exit_code == 0, f"Scheduler remove failed: {result.output}"
    assert "Celery Beat removed." in result.stdout

    assert not PixiRunner().has_dependency("django-celery-beat"), (
        "django-celery-beat still present after removal"
    )
    _assert_beat_app_absent(temp_dir)
    compose_content = (temp_dir / ".devcontainer" / "docker-compose.yaml").read_text()
    assert "celery-beat:" not in compose_content, (
        "celery-beat service still in docker-compose after removal"
    )
    # The celery worker is a dependency, not owned by the scheduler.
    assert ProjectTracking().is_installed(Section.TASK_QUEUE, "celery"), (
        "celery task-queue should not be removed with the scheduler"
    )
    assert not ProjectTracking().is_installed(Section.SCHEDULER, "celery-beat"), (
        "celery-beat still tracked after removal"
    )
