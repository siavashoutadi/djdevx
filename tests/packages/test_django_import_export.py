from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-import-export"


def test_django_import_export_install_and_remove(temp_dir):
    """
    Test django-import-export package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django_import_export",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "django_import_export.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "django_import_export.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    assert PixiRunner().has_dependency("django-import-export"), (
        "Django-import-export dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "django_import_export",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"

    assert not PixiRunner().has_dependency("django-import-export"), (
        "Django-import-export dependency found after removal"
    )
