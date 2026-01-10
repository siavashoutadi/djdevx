from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-taggit"


def test_django_taggit_install_and_remove(temp_dir):
    """
    Test django-taggit package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-taggit",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = backend_dir / "settings" / "packages" / "django_taggit.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "django_taggit.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    assert DjangoProjectManager().has_dependency("django-taggit"), (
        "django-taggit dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-taggit",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"

    assert not DjangoProjectManager().has_dependency("django-taggit"), (
        "django-taggit dependency found after removal"
    )
