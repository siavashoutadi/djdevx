"""Tests for create base-model command."""

import os

from typer.testing import CliRunner

from djdevx.main import app
from tests.test_helpers import create_test_django_project

runner = CliRunner()


def test_create_base_model_defaults(temp_dir):
    """Defaults create a 'core' app with a TimeStampedModel base and register it."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["create", "base-model"])

    assert result.exit_code == 0, f"Create base-model failed: {result.output}"

    models = (temp_dir / "core" / "models.py").read_text()
    assert "class TimeStampedModel(models.Model):" in models
    assert "created_at = models.DateTimeField(auto_now_add=True)" in models
    assert "updated_at = models.DateTimeField(auto_now=True)" in models
    assert "abstract = True" in models

    apps = (temp_dir / "core" / "apps.py").read_text()
    assert "class CoreConfig(AppConfig):" in apps

    settings = (temp_dir / "settings" / "apps" / "core.py").read_text()
    assert '"core",' in settings


def test_create_base_model_custom_names(temp_dir):
    """--app and --class-name customize the generated app and model."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "create",
            "base-model",
            "--app",
            "my_app",
            "--class-name",
            "MyTimestampedModel",
        ],
    )

    assert result.exit_code == 0, f"Create base-model failed: {result.output}"

    models = (temp_dir / "my_app" / "models.py").read_text()
    assert "class MyTimestampedModel(models.Model):" in models

    apps = (temp_dir / "my_app" / "apps.py").read_text()
    assert "class MyAppConfig(AppConfig):" in apps

    settings = (temp_dir / "settings" / "apps" / "my_app.py").read_text()
    assert '"my_app",' in settings


def test_create_base_model_invalid_names(temp_dir):
    """Invalid app/class names must be rejected with a clean error."""
    create_test_django_project(temp_dir, runner)

    for option, value in [("--app", "bad-app"), ("--class-name", "1Bad")]:
        result = runner.invoke(app, ["create", "base-model", option, value])
        assert result.exit_code != 0, f"{option} {value} unexpectedly succeeded"
        assert "is not a valid" in result.output
