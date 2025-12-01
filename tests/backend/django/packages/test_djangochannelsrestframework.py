from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "djangochannelsrestframework"


def test_djangochannelsrestframework_install_and_remove(temp_dir):
    """
    Test djangochannelsrestframework package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # First install channels as it's a dependency
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "channels",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Channels install failed: {result.output}"

    # Now install djangochannelsrestframework
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "djangochannelsrestframework",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = (
        backend_dir / "settings" / "packages" / "djangochannelsrestframework.py"
    )
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "djangochannelsrestframework.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    assert DjangoProjectManager().has_dependency("djangochannelsrestframework"), (
        "djangochannelsrestframework dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "djangochannelsrestframework",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"

    assert not DjangoProjectManager().has_dependency("djangochannelsrestframework"), (
        "djangochannelsrestframework dependency found after removal"
    )


def test_djangochannelsrestframework_install_without_channels(temp_dir):
    """
    Test that djangochannelsrestframework installation fails without channels dependency.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Try to install djangochannelsrestframework without channels
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "djangochannelsrestframework",
            "install",
        ],
    )

    # Should fail with exit code 1
    assert result.exit_code == 1, f"Expected failure, but got: {result.output}"
    assert "'channels' package is a dependency" in result.output, (
        "Missing dependency error not shown"
    )

    # Settings file should not be created
    settings_file = (
        backend_dir / "settings" / "packages" / "djangochannelsrestframework.py"
    )
    assert not settings_file.exists(), (
        "Settings file should not be created when dependency check fails"
    )

    assert not DjangoProjectManager().has_dependency("djangochannelsrestframework"), (
        "djangochannelsrestframework should not be installed when dependency check fails"
    )
