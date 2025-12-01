from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "drf-spectacular"


def test_drf_spectacular_install_and_remove(temp_dir):
    """
    Test drf-spectacular package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # First install djangorestframework since it's a dependency
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
    assert result.exit_code == 0, f"DRF install failed: {result.output}"

    # Now install drf-spectacular
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "drf-spectacular",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    # Check settings file
    settings_file = backend_dir / "settings" / "packages" / "drf_spectacular.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "drf_spectacular.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    # Check URLs file
    urls_file = backend_dir / "urls" / "packages" / "drf_spectacular.py"
    assert urls_file.exists(), "URLs file not created"

    expected_urls_file = DATA_DIR / "urls" / "packages" / "drf_spectacular.py"
    expected_urls_content = expected_urls_file.read_text()
    actual_urls_content = urls_file.read_text()
    assert actual_urls_content == expected_urls_content, "URLs content mismatch"

    assert DjangoProjectManager().has_dependency("drf-spectacular"), (
        "drf-spectacular dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "drf-spectacular",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"

    assert not DjangoProjectManager().has_dependency("drf-spectacular"), (
        "drf-spectacular dependency found after removal"
    )
