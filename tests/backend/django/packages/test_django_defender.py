from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-defender"


def test_django_defender_install_and_remove(temp_dir):
    """
    Test django-defender package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-defender",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = backend_dir / "settings" / "packages" / "django_defender.py"
    assert settings_file.exists(), "Settings file not created"

    urls_file = backend_dir / "urls" / "packages" / "django_defender.py"
    assert urls_file.exists(), "URLs file not created"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "django_defender.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    expected_urls_file = DATA_DIR / "urls" / "packages" / "django_defender.py"
    expected_content = expected_urls_file.read_text()
    actual_content = urls_file.read_text()
    assert actual_content == expected_content, "URLs content mismatch"

    # Check environment variable was set
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "DEFENDER_REDIS_URL" in env_content, "Environment variable not set"
    assert "redis://default:${REDIS_PASSWORD}@cache:6379/1" in env_content, (
        "Environment variable value incorrect"
    )

    assert DjangoProjectManager().has_dependency("django-defender"), (
        "Django-defender dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-defender",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"

    # Check environment variable was removed
    env_content = env_file.read_text()
    assert "DEFENDER_REDIS_URL" not in env_content, "Environment variable not removed"

    assert not DjangoProjectManager().has_dependency("django-defender"), (
        "Django-defender dependency found after removal"
    )
