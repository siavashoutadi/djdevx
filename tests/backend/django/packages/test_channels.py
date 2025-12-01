from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "channels"


def test_channels_install_and_remove(temp_dir):
    """
    Test channels package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

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

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = backend_dir / "settings" / "packages" / "channels.py"
    assert settings_file.exists(), "Settings file not created"

    ws_urls_init_file = backend_dir / "ws_urls" / "__init__.py"
    assert ws_urls_init_file.exists(), "WebSocket URLs file not created"

    asgi_file = backend_dir / "applications" / "asgi.py"
    assert asgi_file.exists(), "ASGI file not found"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "channels.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    expected_ws_urls_file = DATA_DIR / "ws_urls" / "__init__.py"
    expected_content = expected_ws_urls_file.read_text()
    actual_content = ws_urls_init_file.read_text()
    assert actual_content == expected_content, "WebSocket URLs content mismatch"

    expected_asgi_file = DATA_DIR / "applications" / "asgi.py"
    expected_content = expected_asgi_file.read_text()
    actual_content = asgi_file.read_text()
    assert actual_content == expected_content, "ASGI content mismatch"

    devcontainer_env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    assert "CHANNEL_LAYERS_REDIS_HOST" in devcontainer_env_file.read_text()

    assert DjangoProjectManager().has_dependency("channels"), (
        "Channels dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "channels",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not ws_urls_init_file.exists(), "WebSocket URLs file not removed"
    asgi_content = asgi_file.read_text()
    assert expected_content != asgi_content, "ASGI file content is not changed"
    assert "CHANNEL_LAYERS_REDIS_HOST" not in devcontainer_env_file.read_text(), (
        "Devcontainer env not cleaned up"
    )

    assert not DjangoProjectManager().has_dependency("channels"), (
        "Channels dependency found after removal"
    )
