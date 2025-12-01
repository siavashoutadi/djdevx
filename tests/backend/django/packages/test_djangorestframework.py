from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "djangorestframework"


def test_djangorestframework_install_and_remove(temp_dir):
    """
    Test djangorestframework package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "djangorestframework",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    # Check settings file
    settings_file = backend_dir / "settings" / "packages" / "djangorestframework.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "djangorestframework.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    # Check URLs file
    urls_file = backend_dir / "urls" / "packages" / "djangorestframework.py"
    assert urls_file.exists(), "URLs file not created"

    expected_urls_file = DATA_DIR / "urls" / "packages" / "djangorestframework.py"
    expected_urls_content = expected_urls_file.read_text()
    actual_urls_content = urls_file.read_text()
    assert actual_urls_content == expected_urls_content, "URLs content mismatch"

    assert DjangoProjectManager().has_dependency("djangorestframework"), (
        "djangorestframework dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "djangorestframework",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"

    assert not DjangoProjectManager().has_dependency("djangorestframework"), (
        "djangorestframework dependency found after removal"
    )
