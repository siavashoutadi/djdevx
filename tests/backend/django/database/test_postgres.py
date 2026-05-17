"""Tests for PostgreSQL database management."""

import os
from pathlib import Path
from typer.testing import CliRunner

from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "postgres"


def test_postgres_install_and_remove(temp_dir):
    """
    Test PostgreSQL database installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install command
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "database",
            "postgres",
            "install",
        ],
    )

    assert result.exit_code == 0, f"PostgreSQL install failed: {result.output}"
    assert "PostgreSQL database installed successfully!" in result.stdout

    # Check if psycopg2-binary dependency was added
    assert DjangoProjectManager().has_dependency("psycopg2-binary"), (
        "psycopg2-binary dependency not found after installation"
    )

    # Check if database.py settings file exists and matches expected content
    database_settings_file = backend_dir / "settings" / "django" / "database.py"
    assert database_settings_file.exists(), "Database settings file not created"

    database_content = database_settings_file.read_text()
    expected_database_file = (
        DATA_DIR / "backend" / "settings" / "django" / "database.py"
    )
    expected_database_content = expected_database_file.read_text()
    assert database_content == expected_database_content, (
        "Database settings content mismatch"
    )

    # Check if postgres env file was created
    postgres_env_file = temp_dir / ".devcontainer" / ".env" / "postgres"
    assert postgres_env_file.exists(), "Postgres env file not created"

    postgres_env_content = postgres_env_file.read_text()
    expected_postgres_env_file = DATA_DIR / ".devcontainer" / ".env" / "postgres"
    expected_postgres_env_content = expected_postgres_env_file.read_text()
    assert postgres_env_content.strip() == expected_postgres_env_content.strip(), (
        "Postgres env content mismatch"
    )

    # Check if pgadmin env file was created
    pgadmin_env_file = temp_dir / ".devcontainer" / ".env" / "pgadmin"
    assert pgadmin_env_file.exists(), "PgAdmin env file not created"

    pgadmin_env_content = pgadmin_env_file.read_text()
    expected_pgadmin_env_file = DATA_DIR / ".devcontainer" / ".env" / "pgadmin"
    expected_pgadmin_env_content = expected_pgadmin_env_file.read_text()
    assert pgadmin_env_content.strip() == expected_pgadmin_env_content.strip(), (
        "PgAdmin env content mismatch"
    )

    # Check if environment variables were added to devcontainer env
    devcontainer_env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    devcontainer_env_content = devcontainer_env_file.read_text()

    postgres_env_vars = [
        "POSTGRES_SERVER",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "PGDATA",
    ]
    for env_var in postgres_env_vars:
        assert env_var in devcontainer_env_content, (
            f"Environment variable {env_var} not found in devcontainer env"
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

    # Test remove command
    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "database",
            "postgres",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"PostgreSQL remove failed: {result.output}"
    assert "PostgreSQL database removed successfully!" in result.stdout

    # Check if psycopg2-binary dependency was removed
    assert not DjangoProjectManager().has_dependency("psycopg2-binary"), (
        "psycopg2-binary dependency found after removal"
    )

    # Check if postgres env file was removed
    assert not postgres_env_file.exists(), "Postgres env file not removed"

    # Check if pgadmin env file was removed
    assert not pgadmin_env_file.exists(), "PgAdmin env file not removed"

    # Check if environment variables were removed from devcontainer env
    devcontainer_env_content = devcontainer_env_file.read_text()
    for env_var in postgres_env_vars:
        assert env_var not in devcontainer_env_content, (
            f"Environment variable {env_var} still found in devcontainer env after removal"
        )

    # Check if postgres service was removed from docker-compose
    docker_compose_content = docker_compose_file.read_text()
    assert "db:" not in docker_compose_content, (
        "Postgres service 'db' still found in docker-compose after removal"
    )
    assert "pgadmin" not in docker_compose_content, (
        "PgAdmin service still found in docker-compose after removal"
    )
