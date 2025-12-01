from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django_storages"


def test_django_storages_s3_install_and_remove(temp_dir):
    """
    Test django-storages S3 backend package installation and removal.
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
            "django-storages",
            "s3",
            "install",
            "--access-key",
            "test-access-key",
            "--secret-key",
            "test-secret-key",
            "--region-name",
            "us-east-1",
            "--bucket-name",
            "test-bucket",
        ],
    )

    assert result.exit_code == 0
    assert "django-storages with S3 backend is installed successfully." in result.stdout

    # Check if package is installed
    assert DjangoProjectManager().has_dependency("django-storages")

    # Check if settings file is created
    settings_file = backend_dir / "settings" / "packages" / "django_storages_s3.py"
    assert settings_file.exists()

    # Check settings content with expected S3 configuration
    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "s3" / "settings" / "packages" / "django_storages_s3.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    # Check if env file is updated
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "STORAGES_S3_ACCESS_KEY=test-access-key" in env_content
    assert "STORAGES_S3_SECRET_KEY=test-secret-key" in env_content
    assert "STORAGES_S3_REGION_NAME=us-east-1" in env_content
    assert "STORAGES_S3_BUCKET_NAME=test-bucket" in env_content

    # Test remove
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-storages", "s3", "remove"]
    )

    assert result.exit_code == 0
    assert "django-storages S3 backend is removed successfully." in result.stdout

    # Check if package is removed
    assert not DjangoProjectManager().has_dependency("django-storages")

    # Check if files are removed
    assert not settings_file.exists()


def test_django_storages_azure_install_and_remove(temp_dir):
    """
    Test django-storages Azure backend package installation and removal.
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
            "django-storages",
            "azure",
            "install",
            "--account-key",
            "test-account-key",
            "--account-name",
            "test-account-name",
            "--container-name",
            "test-container",
        ],
    )

    assert result.exit_code == 0
    assert (
        "django-storages with Azure backend is installed successfully." in result.stdout
    )

    # Check if package is installed
    assert DjangoProjectManager().has_dependency("django-storages")

    # Check if settings file is created
    settings_file = backend_dir / "settings" / "packages" / "django_storages_azure.py"
    assert settings_file.exists()

    # Check settings content with expected Azure configuration
    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "azure" / "settings" / "packages" / "django_storages_azure.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    # Check if env file is updated
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "STORAGES_AZURE_ACCOUNT_KEY=test-account-key" in env_content
    assert "STORAGES_AZURE_ACCOUNT_NAME=test-account-name" in env_content
    assert "STORAGES_AZURE_CONTAINER_NAME=test-container" in env_content

    # Test remove
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-storages", "azure", "remove"]
    )

    assert result.exit_code == 0
    assert "django-storages Azure backend is removed successfully." in result.stdout

    # Check if package is removed
    assert not DjangoProjectManager().has_dependency("django-storages")

    # Check if files are removed
    assert not settings_file.exists()


def test_django_storages_google_install_and_remove(temp_dir):
    """
    Test django-storages Google backend package installation and removal.
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
            "django-storages",
            "google",
            "install",
            "--credentials-file-path",
            "/path/to/credentials.json",
            "--bucket-name",
            "test-google-bucket",
        ],
    )

    assert result.exit_code == 0
    assert (
        "django-storages with Google backend is installed successfully."
        in result.stdout
    )

    # Check if package is installed
    assert DjangoProjectManager().has_dependency("django-storages")

    # Check if settings file is created
    settings_file = backend_dir / "settings" / "packages" / "django_storages_google.py"
    assert settings_file.exists()

    # Check settings content with expected Google configuration
    settings_content = settings_file.read_text()
    expected_settings = (
        DATA_DIR / "google" / "settings" / "packages" / "django_storages_google.py"
    ).read_text()
    assert settings_content.strip() == expected_settings.strip()

    # Check if env file is updated
    env_file = temp_dir / ".devcontainer" / ".env" / "devcontainer"
    env_content = env_file.read_text()
    assert "STORAGES_GOOGLE_CREDENTIALS=/path/to/credentials.json" in env_content
    assert "STORAGES_GOOGLE_BUCKET_NAME=test-google-bucket" in env_content

    # Test remove
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-storages", "google", "remove"]
    )

    assert result.exit_code == 0
    assert "django-storages Google backend is removed successfully." in result.stdout

    # Check if package is removed
    assert not DjangoProjectManager().has_dependency("django-storages")

    # Check if files are removed
    assert not settings_file.exists()
