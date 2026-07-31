from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django_anymail"


def test_django_anymail_ses_install_and_remove(temp_dir):
    """
    Test django-anymail SES backend package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-anymail",
            "--provider",
            "ses",
        ],
    )

    assert result.exit_code == 0
    assert "Django Anymail (Amazon SES) installed." in result.stdout

    assert PixiRunner().has_dependency("django-anymail")

    settings_file = temp_dir / "settings" / "packages" / "django_anymail_ses.py"
    assert settings_file.exists()

    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "ses" / "settings" / "packages" / "django_anymail_ses.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    result = runner.invoke(
        app, ["packages", "remove", "django-anymail", "--provider", "ses"]
    )

    assert result.exit_code == 0
    assert "Django Anymail removed." in result.stdout

    assert not PixiRunner().has_dependency("django-anymail")
    assert not settings_file.exists()


def test_django_anymail_brevo_install_and_remove(temp_dir):
    """
    Test django-anymail Brevo backend package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-anymail",
            "--provider",
            "brevo",
        ],
    )

    assert result.exit_code == 0
    assert "Django Anymail (Brevo) installed." in result.stdout

    assert PixiRunner().has_dependency("django-anymail")

    settings_file = temp_dir / "settings" / "packages" / "django_anymail_brevo.py"
    assert settings_file.exists()

    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "brevo" / "settings" / "packages" / "django_anymail_brevo.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    result = runner.invoke(
        app, ["packages", "remove", "django-anymail", "--provider", "brevo"]
    )

    assert result.exit_code == 0
    assert "Django Anymail removed." in result.stdout

    assert not PixiRunner().has_dependency("django-anymail")
    assert not settings_file.exists()


def test_django_anymail_mailgun_install_and_remove(temp_dir):
    """
    Test django-anymail Mailgun backend package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-anymail",
            "--provider",
            "mailgun",
        ],
    )

    assert result.exit_code == 0
    assert "Django Anymail (Mailgun) installed." in result.stdout

    assert PixiRunner().has_dependency("django-anymail")

    settings_file = temp_dir / "settings" / "packages" / "django_anymail_mailgun.py"
    assert settings_file.exists()

    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "mailgun" / "settings" / "packages" / "django_anymail_mailgun.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    result = runner.invoke(
        app, ["packages", "remove", "django-anymail", "--provider", "mailgun"]
    )

    assert result.exit_code == 0
    assert "Django Anymail removed." in result.stdout

    assert not PixiRunner().has_dependency("django-anymail")
    assert not settings_file.exists()


def test_django_anymail_mailjet_install_and_remove(temp_dir):
    """
    Test django-anymail Mailjet backend package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-anymail",
            "--provider",
            "mailjet",
        ],
    )

    assert result.exit_code == 0
    assert "Django Anymail (Mailjet) installed." in result.stdout

    assert PixiRunner().has_dependency("django-anymail")

    settings_file = temp_dir / "settings" / "packages" / "django_anymail_mailjet.py"
    assert settings_file.exists()

    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "mailjet" / "settings" / "packages" / "django_anymail_mailjet.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    result = runner.invoke(
        app, ["packages", "remove", "django-anymail", "--provider", "mailjet"]
    )

    assert result.exit_code == 0
    assert "Django Anymail removed." in result.stdout

    assert not PixiRunner().has_dependency("django-anymail")
    assert not settings_file.exists()


def test_django_anymail_resend_install_and_remove(temp_dir):
    """
    Test django-anymail Resend backend package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-anymail",
            "--provider",
            "resend",
        ],
    )

    assert result.exit_code == 0
    assert "Django Anymail (Resend) installed." in result.stdout

    assert PixiRunner().has_dependency("django-anymail")

    settings_file = temp_dir / "settings" / "packages" / "django_anymail_resend.py"
    assert settings_file.exists()

    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "resend" / "settings" / "packages" / "django_anymail_resend.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    result = runner.invoke(
        app, ["packages", "remove", "django-anymail", "--provider", "resend"]
    )

    assert result.exit_code == 0
    assert "Django Anymail removed." in result.stdout

    assert not PixiRunner().has_dependency("django-anymail")
    assert not settings_file.exists()
