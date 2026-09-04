from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.core.process import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-health-check"


def test_django_health_check_install_and_remove(temp_dir):
    """
    Test django-health-check package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django_health_check",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "django_health_check.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "django_health_check.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    urls_file = temp_dir / "urls" / "packages" / "django_health_check.py"
    assert urls_file.exists(), "URLs file not created"

    expected_urls_file = DATA_DIR / "urls" / "packages" / "django_health_check.py"
    expected_urls_content = expected_urls_file.read_text()
    assert urls_file.read_text() == expected_urls_content, "URLs content mismatch"

    assert PixiRunner().has_dependency("django-health-check"), (
        "django-health-check dependency not found after installation"
    )
    assert PixiRunner().has_dependency("psutil"), (
        "psutil dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "django_health_check",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"

    assert not PixiRunner().has_dependency("django-health-check"), (
        "django-health-check dependency found after removal"
    )
    assert not PixiRunner().has_dependency("psutil"), (
        "psutil dependency found after removal"
    )
