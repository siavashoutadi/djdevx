from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-oauth-toolkit"


def test_django_oauth_toolkit_install_and_remove(temp_dir):
    """
    Test django-oauth-toolkit package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-oauth-toolkit",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = backend_dir / "settings" / "packages" / "django_oauth_toolkit.py"
    assert settings_file.exists(), "Settings file not created"

    urls_file = backend_dir / "urls" / "packages" / "django_oauth_toolkit.py"
    assert urls_file.exists(), "URLs file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "django_oauth_toolkit.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    expected_urls_file = DATA_DIR / "urls" / "packages" / "django_oauth_toolkit.py"
    expected_content = expected_urls_file.read_text()
    actual_content = urls_file.read_text()
    assert actual_content == expected_content, "URLs content mismatch"

    assert DjangoProjectManager().has_dependency("django-oauth-toolkit"), (
        "Django-oauth-toolkit dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-oauth-toolkit",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not urls_file.exists(), "URLs file not removed"

    assert not DjangoProjectManager().has_dependency("django-oauth-toolkit"), (
        "Django-oauth-toolkit dependency found after removal"
    )
