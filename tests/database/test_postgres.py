"""Tests for PostgreSQL database management."""

import os
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from djdevx.main import app
from djdevx.core.process import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "postgres"


def test_postgres_install_and_remove(temp_dir):
    """
    Test PostgreSQL database installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install command
    result = runner.invoke(
        app,
        [
            "database",
            "add",
            "postgres",
        ],
    )

    assert result.exit_code == 0, f"PostgreSQL install failed: {result.output}"
    assert "PostgreSQL installed." in result.stdout

    # Check if psycopg2-binary dependency was added
    assert PixiRunner().has_dependency("psycopg2-binary"), (
        "psycopg2-binary dependency not found after installation"
    )

    # Check if database.py settings file exists and matches expected content
    database_settings_file = temp_dir / "settings" / "django" / "database.py"
    assert database_settings_file.exists(), "Database settings file not created"

    database_content = database_settings_file.read_text()
    expected_database_file = (
        DATA_DIR / "backend" / "settings" / "django" / "database.py"
    )
    expected_database_content = expected_database_file.read_text()
    assert database_content == expected_database_content, (
        "Database settings content mismatch"
    )

    # Check if docker-compose.yaml has postgres service
    docker_compose_file = temp_dir / ".devcontainer" / "docker-compose.yaml"
    assert docker_compose_file.exists(), "docker-compose.yaml file not found"

    docker_compose_content = docker_compose_file.read_text()
    assert "db:" in docker_compose_content, (
        "Postgres service 'db' not found in docker-compose"
    )
    assert "postgres:16" in docker_compose_content, (
        "Postgres image not found in docker-compose"
    )
    assert "pgadmin" in docker_compose_content, (
        "PgAdmin service not found in docker-compose"
    )
    assert "app-db-data" in docker_compose_content, (
        "Database volume not found in docker-compose"
    )

    # Test remove command — mock questionary to select postgres
    os.chdir(temp_dir)
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "postgres"
        result = runner.invoke(
            app,
            [
                "database",
                "remove",
            ],
        )

    assert result.exit_code == 0, f"PostgreSQL remove failed: {result.output}"
    assert "PostgreSQL removed." in result.stdout

    # Check if psycopg2-binary dependency was removed
    assert not PixiRunner().has_dependency("psycopg2-binary"), (
        "psycopg2-binary dependency found after removal"
    )

    # Check if postgres service was removed from docker-compose
    docker_compose_content = docker_compose_file.read_text()
    assert "db:" not in docker_compose_content, (
        "Postgres service 'db' still found in docker-compose after removal"
    )
    assert "pgadmin" not in docker_compose_content, (
        "PgAdmin service still found in docker-compose after removal"
    )

    # Check if database.py was restored to the default sqlite template
    database_content_after = database_settings_file.read_text()
    default_database_file = (
        Path(__file__).parent.parent.parent
        / "djdevx"
        / "new"
        / "templates"
        / "settings"
        / "django"
        / "database.py"
    )
    assert database_content_after == default_database_file.read_text(), (
        "database.py not restored to default sqlite settings after removal"
    )
