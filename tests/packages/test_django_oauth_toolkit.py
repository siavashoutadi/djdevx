from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-oauth-toolkit"


def test_django_oauth_toolkit_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["packages", "add", "django_oauth_toolkit"])
    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "django_oauth_toolkit.py"
    assert settings_file.exists(), "Settings file not created"

    expected_content = (
        DATA_DIR / "settings" / "packages" / "django_oauth_toolkit.py"
    ).read_text()
    assert settings_file.read_text() == expected_content

    urls_file = temp_dir / "urls" / "packages" / "django_oauth_toolkit.py"
    assert urls_file.exists(), "URLs file not created"

    expected_urls_content = (
        DATA_DIR / "urls" / "packages" / "django_oauth_toolkit.py"
    ).read_text()
    assert urls_file.read_text() == expected_urls_content

    assert PixiRunner().has_dependency("django-oauth-toolkit")

    result = runner.invoke(app, ["packages", "remove", "django_oauth_toolkit"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"
    assert not PixiRunner().has_dependency("django-oauth-toolkit")
