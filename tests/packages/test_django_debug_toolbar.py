from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-debug-toolbar"


def test_django_debug_toolbar_install_and_remove(temp_dir):
    """
    Test django-debug-toolbar package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-debug-toolbar",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "django_debug_toolbar.py"
    assert settings_file.exists(), "Settings file not created"

    urls_file = temp_dir / "urls" / "packages" / "django_debug_toolbar.py"
    assert urls_file.exists(), "URLs file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "django_debug_toolbar.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    expected_urls_file = DATA_DIR / "urls" / "packages" / "django_debug_toolbar.py"
    expected_content = expected_urls_file.read_text()
    actual_content = urls_file.read_text()
    assert actual_content == expected_content, "URLs content mismatch"

    assert "django-debug-toolbar" in PixiRunner().list_dependencies(
        environment="dev"
    ), "Django-debug-toolbar dependency not found after installation"

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "django-debug-toolbar",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"

    assert not PixiRunner().has_dependency("django-debug-toolbar", environment="dev"), (
        "Django-debug-toolbar dependency found after removal"
    )
