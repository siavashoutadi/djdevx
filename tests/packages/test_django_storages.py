from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.core.process import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django_storages"


def test_django_storages_s3_install_and_remove(temp_dir):
    """
    Test django-storages S3 backend package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-storages",
            "--provider",
            "s3",
        ],
    )

    assert result.exit_code == 0
    assert "Django Storages (Amazon S3) installed." in result.stdout

    assert PixiRunner().has_dependency("django-storages")

    settings_file = temp_dir / "settings" / "packages" / "django_storages_s3.py"
    assert settings_file.exists()

    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "s3" / "settings" / "packages" / "django_storages_s3.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    result = runner.invoke(
        app, ["packages", "remove", "django-storages", "--provider", "s3"]
    )

    assert result.exit_code == 0
    assert "Django Storages" in result.stdout and "removed." in result.stdout

    assert not PixiRunner().has_dependency("django-storages")
    assert not settings_file.exists()


def test_django_storages_azure_install_and_remove(temp_dir):
    """
    Test django-storages Azure backend package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-storages",
            "--provider",
            "azure",
        ],
    )

    assert result.exit_code == 0
    assert "Django Storages (Azure Blob Storage) installed." in result.stdout

    assert PixiRunner().has_dependency("django-storages")

    settings_file = temp_dir / "settings" / "packages" / "django_storages_azure.py"
    assert settings_file.exists()

    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "azure" / "settings" / "packages" / "django_storages_azure.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    result = runner.invoke(
        app, ["packages", "remove", "django-storages", "--provider", "azure"]
    )

    assert result.exit_code == 0
    assert "Django Storages" in result.stdout and "removed." in result.stdout

    assert not PixiRunner().has_dependency("django-storages")
    assert not settings_file.exists()


def test_django_storages_google_install_and_remove(temp_dir):
    """
    Test django-storages Google Cloud Storage backend package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django-storages",
            "--provider",
            "google",
        ],
    )

    assert result.exit_code == 0
    assert "Django Storages (Google Cloud Storage) installed." in result.stdout

    assert PixiRunner().has_dependency("django-storages")

    settings_file = temp_dir / "settings" / "packages" / "django_storages_google.py"
    assert settings_file.exists()

    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "google" / "settings" / "packages" / "django_storages_google.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    result = runner.invoke(
        app, ["packages", "remove", "django-storages", "--provider", "google"]
    )

    assert result.exit_code == 0
    assert "Django Storages" in result.stdout and "removed." in result.stdout

    assert not PixiRunner().has_dependency("django-storages")
    assert not settings_file.exists()
