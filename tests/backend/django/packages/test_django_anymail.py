from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django_anymail"


def test_django_anymail_ses_install_and_remove(temp_dir):
    """
    Test django-anymail SES backend package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install with specific values for templating
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-anymail",
            "ses",
            "install",
            "--access-key",
            "test-access-key",
            "--secret-key",
            "test-secret-key",
            "--region-name",
            "us-east-1",
            "--default-from-email",
            "noreply@example.com",
        ],
    )

    assert result.exit_code == 0
    assert "django-anymail with SES backend is installed successfully." in result.stdout

    # Check if package is installed
    assert DjangoProjectManager().has_dependency("django-anymail")

    # Check if settings file is created
    settings_file = backend_dir / "settings" / "packages" / "django_anymail_ses.py"
    assert settings_file.exists()

    # Check settings content with expected SES configuration
    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "ses" / "settings" / "packages" / "django_anymail_ses.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    # Check if env file is updated
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "ANYMAIL_SES_ACCESS_KEY=test-access-key" in env_content
    assert "ANYMAIL_SES_SECRET_KEY=test-secret-key" in env_content
    assert "ANYMAIL_SES_REGION_NAME=us-east-1" in env_content
    assert "DEFAULT_FROM_EMAIL=noreply@example.com" in env_content

    # Test remove
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-anymail", "ses", "remove"]
    )

    assert result.exit_code == 0
    assert "django-anymail SES backend is removed successfully." in result.stdout

    # Check if package is removed
    assert not DjangoProjectManager().has_dependency("django-anymail")

    # Check if files are removed
    assert not settings_file.exists()


def test_django_anymail_brevo_install_and_remove(temp_dir):
    """
    Test django-anymail Brevo backend package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install with specific values for templating
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-anymail",
            "brevo",
            "install",
            "--api-key",
            "test-brevo-api-key",
            "--default-from-email",
            "noreply@example.com",
        ],
    )

    assert result.exit_code == 0
    assert (
        "django-anymail with Brevo backend is installed successfully." in result.stdout
    )

    # Check if package is installed
    assert DjangoProjectManager().has_dependency("django-anymail")

    # Check if settings file is created
    settings_file = backend_dir / "settings" / "packages" / "django_anymail_brevo.py"
    assert settings_file.exists()

    # Check settings content with expected Brevo configuration
    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "brevo" / "settings" / "packages" / "django_anymail_brevo.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    # Check if env file is updated
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "ANYMAIL_BREVO_API_KEY=test-brevo-api-key" in env_content
    assert "DEFAULT_FROM_EMAIL=noreply@example.com" in env_content

    # Test remove
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-anymail", "brevo", "remove"]
    )

    assert result.exit_code == 0
    assert "django-anymail Brevo backend is removed successfully." in result.stdout

    # Check if package is removed
    assert not DjangoProjectManager().has_dependency("django-anymail")

    # Check if files are removed
    assert not settings_file.exists()


def test_django_anymail_mailgun_install_and_remove(temp_dir):
    """
    Test django-anymail Mailgun backend package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install with specific values for templating
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-anymail",
            "mailgun",
            "install",
            "--api-key",
            "test-mailgun-api-key",
            "--domain",
            "test-domain.com",
            "--default-from-email",
            "noreply@example.com",
        ],
    )

    assert result.exit_code == 0
    assert (
        "django-anymail with Mailgun backend is installed successfully."
        in result.stdout
    )

    # Check if package is installed
    assert DjangoProjectManager().has_dependency("django-anymail")

    # Check if settings file is created
    settings_file = backend_dir / "settings" / "packages" / "django_anymail_mailgun.py"
    assert settings_file.exists()

    # Check settings content with expected Mailgun configuration
    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "mailgun" / "settings" / "packages" / "django_anymail_mailgun.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    # Check if env file is updated
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "ANYMAIL_MAILGUN_API_KEY=test-mailgun-api-key" in env_content
    assert "ANYMAIL_MAILGUN_SENDER_DOMAIN=test-domain.com" in env_content
    assert "DEFAULT_FROM_EMAIL=noreply@example.com" in env_content

    # Test remove
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-anymail", "mailgun", "remove"]
    )

    assert result.exit_code == 0
    assert "django-anymail Mailgun backend is removed successfully." in result.stdout

    # Check if package is removed
    assert not DjangoProjectManager().has_dependency("django-anymail")

    # Check if files are removed
    assert not settings_file.exists()


def test_django_anymail_mailjet_install_and_remove(temp_dir):
    """
    Test django-anymail Mailjet backend package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install with specific values for templating
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-anymail",
            "mailjet",
            "install",
            "--api-key",
            "test-mailjet-api-key",
            "--secret-key",
            "test-mailjet-secret-key",
            "--default-from-email",
            "noreply@example.com",
        ],
    )

    assert result.exit_code == 0
    assert (
        "django-anymail with Mailjet backend is installed successfully."
        in result.stdout
    )

    # Check if package is installed
    assert DjangoProjectManager().has_dependency("django-anymail")

    # Check if settings file is created
    settings_file = backend_dir / "settings" / "packages" / "django_anymail_mailjet.py"
    assert settings_file.exists()

    # Check settings content with expected Mailjet configuration
    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "mailjet" / "settings" / "packages" / "django_anymail_mailjet.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    # Check if env file is updated
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "ANYMAIL_MAILJET_API_KEY=test-mailjet-api-key" in env_content
    assert "ANYMAIL_MAILJET_SECRET_KEY=test-mailjet-secret-key" in env_content
    assert "DEFAULT_FROM_EMAIL=noreply@example.com" in env_content

    # Test remove
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-anymail", "mailjet", "remove"]
    )

    assert result.exit_code == 0
    assert "django-anymail Mailjet backend is removed successfully." in result.stdout

    # Check if package is removed
    assert not DjangoProjectManager().has_dependency("django-anymail")

    # Check if files are removed
    assert not settings_file.exists()


def test_django_anymail_resend_install_and_remove(temp_dir):
    """
    Test django-anymail Resend backend package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Test install with specific values for templating
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-anymail",
            "resend",
            "install",
            "--api-key",
            "test-resend-api-key",
            "--default-from-email",
            "noreply@example.com",
        ],
    )

    assert result.exit_code == 0
    assert (
        "django-anymail with Resend backend is installed successfully." in result.stdout
    )

    # Check if package is installed
    assert DjangoProjectManager().has_dependency("django-anymail")

    # Check if settings file is created
    settings_file = backend_dir / "settings" / "packages" / "django_anymail_resend.py"
    assert settings_file.exists()

    # Check settings content with expected Resend configuration
    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "resend" / "settings" / "packages" / "django_anymail_resend.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    # Check if env file is updated
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "ANYMAIL_RESEND_API_KEY=test-resend-api-key" in env_content
    assert "DEFAULT_FROM_EMAIL=noreply@example.com" in env_content

    # Test remove
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-anymail", "resend", "remove"]
    )

    assert result.exit_code == 0
    assert "django-anymail Resend backend is removed successfully." in result.stdout

    # Check if package is removed
    assert not DjangoProjectManager().has_dependency("django-anymail")

    # Check if files are removed
    assert not settings_file.exists()
