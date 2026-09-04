"""Tests for Redis cache management."""

import os
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from djdevx.main import app
from djdevx.core.process import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "redis"


def test_redis_install_and_remove(temp_dir):
    """
    Test Redis cache installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install command
    result = runner.invoke(
        app,
        [
            "cache",
            "add",
            "redis",
        ],
    )

    assert result.exit_code == 0, f"Redis cache install failed: {result.output}"
    assert "Redis installed." in result.stdout

    # Check if django-redis dependency was added
    assert PixiRunner().has_dependency("django-redis"), (
        "django-redis dependency not found after installation"
    )

    # Check if caches.py settings file exists and matches expected content
    caches_settings_file = temp_dir / "settings" / "django" / "caches.py"
    assert caches_settings_file.exists(), "Cache settings file not created"

    caches_content = caches_settings_file.read_text()
    expected_caches_file = DATA_DIR / "backend" / "settings" / "django" / "caches.py"
    expected_caches_content = expected_caches_file.read_text()
    assert caches_content == expected_caches_content, "Cache settings content mismatch"

    # Check if sessions.py settings file exists and matches expected content
    sessions_settings_file = temp_dir / "settings" / "django" / "sessions.py"
    assert sessions_settings_file.exists(), "Sessions settings file not found"

    sessions_content = sessions_settings_file.read_text()
    expected_sessions_file = (
        DATA_DIR / "backend" / "settings" / "django" / "sessions.py"
    )
    expected_sessions_content = expected_sessions_file.read_text()
    assert sessions_content == expected_sessions_content, (
        "Sessions settings content mismatch"
    )

    # Check if docker-compose.yaml has redis service
    docker_compose_file = temp_dir / ".devcontainer" / "docker-compose.yaml"
    assert docker_compose_file.exists(), "docker-compose.yaml file not found"

    docker_compose_content = docker_compose_file.read_text()
    assert "\n  cache:" in docker_compose_content, (
        "Redis service 'cache' not found in docker-compose"
    )
    assert "redis:7.4-alpine" in docker_compose_content, (
        "Redis image not found in docker-compose"
    )
    assert "cache-data" in docker_compose_content, (
        "Redis volume not found in docker-compose"
    )

    # Test remove command — mock questionary to select redis
    os.chdir(temp_dir)
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "redis"
        result = runner.invoke(
            app,
            [
                "cache",
                "remove",
            ],
        )

    assert result.exit_code == 0, f"Redis cache remove failed: {result.output}"
    assert "Redis removed." in result.stdout

    # Check if django-redis dependency was removed
    assert not PixiRunner().has_dependency("django-redis"), (
        "django-redis dependency found after removal"
    )

    # Check if caches.py settings file was removed
    assert not caches_settings_file.exists(), "Cache settings file not removed"

    # Check if sessions.py was restored to default (no cached_db)
    sessions_content_after = sessions_settings_file.read_text()
    assert "cached_db" not in sessions_content_after, (
        "sessions.py still references cached_db after removal"
    )

    # Check if redis service was removed from docker-compose
    docker_compose_content = docker_compose_file.read_text()
    assert "\n  cache:" not in docker_compose_content, (
        "Redis service 'cache' still found in docker-compose after removal"
    )
    assert "cache-data" not in docker_compose_content, (
        "Redis volume still found in docker-compose after removal"
    )
