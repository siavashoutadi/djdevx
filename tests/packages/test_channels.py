from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "channels"


def test_channels_install_and_remove(temp_dir):
    """
    Test channels package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "channels",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "channels.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "channels.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    ws_urls_init = temp_dir / "ws_urls" / "__init__.py"
    assert ws_urls_init.exists(), "ws_urls/__init__.py not created"

    asgi_file = temp_dir / "applications" / "asgi.py"
    assert asgi_file.exists(), "applications/asgi.py not created"

    expected_asgi = DATA_DIR / "applications" / "asgi.py"
    expected_asgi_content = expected_asgi.read_text()
    assert asgi_file.read_text() == expected_asgi_content, (
        "applications/asgi.py content mismatch"
    )

    assert PixiRunner().has_dependency("channels"), (
        "channels dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "channels",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"

    assert not PixiRunner().has_dependency("channels"), (
        "channels dependency found after removal"
    )
