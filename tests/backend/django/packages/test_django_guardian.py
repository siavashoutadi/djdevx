from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-guardian"


def test_django_guardian_install_and_remove(temp_dir):
    """
    Test django-guardian package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Check initial User model state
    user_model_file = backend_dir / "users" / "models.py"
    initial_user_content = user_model_file.read_text()
    assert "GuardianUserMixin" not in initial_user_content, (
        "GuardianUserMixin already present before install"
    )

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-guardian",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = backend_dir / "settings" / "packages" / "django_guardian.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "django_guardian.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    # Check User model was modified
    user_content = user_model_file.read_text()
    assert "from guardian.mixins import GuardianUserMixin" in user_content, (
        "GuardianUserMixin import not added"
    )
    assert "class User(AbstractUser, GuardianUserMixin):" in user_content, (
        "GuardianUserMixin not added to User class"
    )

    assert DjangoProjectManager().has_dependency("django-guardian"), (
        "Django-guardian dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-guardian",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"

    # Check User model was reverted
    user_content = user_model_file.read_text()
    assert "from guardian.mixins import GuardianUserMixin" not in user_content, (
        "GuardianUserMixin import not removed"
    )
    assert "class User(AbstractUser, GuardianUserMixin):" not in user_content, (
        "GuardianUserMixin not removed from User class"
    )
    assert "class User(AbstractUser):" in user_content, (
        "User class definition corrupted"
    )

    assert not DjangoProjectManager().has_dependency("django-guardian"), (
        "Django-guardian dependency found after removal"
    )
