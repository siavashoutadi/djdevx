from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "djangorestframework"


def test_djangorestframework_install_and_remove(temp_dir):
    """
    Test djangorestframework package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "djangorestframework",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "djangorestframework.py"
    assert settings_file.exists(), "Settings file not created"

    urls_file = temp_dir / "urls" / "packages" / "djangorestframework.py"
    assert urls_file.exists(), "URLs file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "djangorestframework.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    expected_urls_file = DATA_DIR / "urls" / "packages" / "djangorestframework.py"
    expected_content = expected_urls_file.read_text()
    actual_content = urls_file.read_text()
    assert actual_content == expected_content, "URLs content mismatch"

    assert PixiRunner().has_dependency("djangorestframework"), (
        "djangorestframework dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "djangorestframework",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"

    assert not PixiRunner().has_dependency("djangorestframework"), (
        "djangorestframework dependency found after removal"
    )
