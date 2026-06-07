"""Tests for STORAGES.update() behavior when multiple storage packages are installed."""

from pathlib import Path
import os
import pytest
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
WHITENOISE_DATA = Path(__file__).parent / "data" / "whitenoise"
S3_DATA = Path(__file__).parent / "data" / "django_storages" / "s3"
AZURE_DATA = Path(__file__).parent / "data" / "django_storages" / "azure"
GOOGLE_DATA = Path(__file__).parent / "data" / "django_storages" / "google"


# ── Combined install tests ─────────────────────────────────────────────────


def test_whitenoise_plus_s3(temp_dir):
    """Install whitenoise then django-storages S3 — both settings files coexist."""
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Install whitenoise
    result = runner.invoke(
        app, ["backend", "django", "packages", "whitenoise", "install"]
    )
    assert result.exit_code == 0, f"whitenoise install failed: {result.output}"

    whitenoise_file = backend_dir / "settings" / "packages" / "whitenoise.py"
    assert whitenoise_file.exists()

    whitenoise_expected = (
        WHITENOISE_DATA / "settings" / "packages" / "whitenoise.py"
    ).read_text()
    assert whitenoise_file.read_text() == whitenoise_expected

    # Install django-storages S3
    result = runner.invoke(
        app, ["backend", "django", "packages", "django-storages", "s3", "install"]
    )
    assert result.exit_code == 0, f"S3 install failed: {result.output}"

    s3_file = backend_dir / "settings" / "packages" / "django_storages_s3.py"
    assert s3_file.exists()

    s3_expected = (
        S3_DATA / "settings" / "packages" / "django_storages_s3.py"
    ).read_text()
    assert s3_file.read_text().strip() == s3_expected.strip()

    # Both files still present
    assert whitenoise_file.exists()

    # Both dependencies installed
    assert DjangoProjectManager().has_dependency("whitenoise")
    assert DjangoProjectManager().has_dependency("django-storages")


def test_whitenoise_plus_azure(temp_dir):
    """Install whitenoise then django-storages Azure."""
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app, ["backend", "django", "packages", "whitenoise", "install"]
    )
    assert result.exit_code == 0, f"whitenoise install failed: {result.output}"

    result = runner.invoke(
        app, ["backend", "django", "packages", "django-storages", "azure", "install"]
    )
    assert result.exit_code == 0, f"Azure install failed: {result.output}"

    azure_file = backend_dir / "settings" / "packages" / "django_storages_azure.py"
    assert azure_file.exists()

    azure_expected = (
        AZURE_DATA / "settings" / "packages" / "django_storages_azure.py"
    ).read_text()
    assert azure_file.read_text().strip() == azure_expected.strip()

    assert DjangoProjectManager().has_dependency("whitenoise")
    assert DjangoProjectManager().has_dependency("django-storages")


def test_whitenoise_plus_google(temp_dir):
    """Install whitenoise then django-storages Google Cloud Storage."""
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app, ["backend", "django", "packages", "whitenoise", "install"]
    )
    assert result.exit_code == 0, f"whitenoise install failed: {result.output}"

    result = runner.invoke(
        app, ["backend", "django", "packages", "django-storages", "google", "install"]
    )
    assert result.exit_code == 0, f"Google install failed: {result.output}"

    google_file = backend_dir / "settings" / "packages" / "django_storages_google.py"
    assert google_file.exists()

    google_expected = (
        GOOGLE_DATA / "settings" / "packages" / "django_storages_google.py"
    ).read_text()
    assert google_file.read_text().strip() == google_expected.strip()

    assert DjangoProjectManager().has_dependency("whitenoise")
    assert DjangoProjectManager().has_dependency("django-storages")


# ── exec() namespace simulation tests ──────────────────────────────────────


def test_exec_base_storages_has_default_key(temp_dir):
    """Simulate exec() of base storages.py alone — must have 'default' and 'staticfiles'."""
    namespace = {}
    code = """STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}"""
    exec(code, namespace)
    assert "default" in namespace["STORAGES"]
    assert (
        namespace["STORAGES"]["default"]["BACKEND"]
        == "django.core.files.storage.FileSystemStorage"
    )
    assert "staticfiles" in namespace["STORAGES"]


def test_exec_whitenoise_updates_staticfiles(temp_dir):
    """Simulate base + whitenoise exec — staticfiles is whitenoise, default preserved."""
    namespace = {}
    exec(
        """STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}""",
        namespace,
    )
    exec(
        """STORAGES.update({
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
})""",
        namespace,
    )

    storages = namespace["STORAGES"]
    assert "default" in storages
    assert (
        storages["default"]["BACKEND"] == "django.core.files.storage.FileSystemStorage"
    )
    assert (
        storages["staticfiles"]["BACKEND"]
        == "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )


def test_exec_whitenoise_then_s3(temp_dir):
    """Simulate base + whitenoise + S3 exec — S3 wins for both keys."""
    namespace = {}
    exec(
        """STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}""",
        namespace,
    )
    exec(
        """STORAGES.update({
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
})""",
        namespace,
    )
    exec(
        """STORAGES.update({
    "default": {"BACKEND": "storages.backends.s3.S3Storage", "OPTIONS": {}},
    "staticfiles": {"BACKEND": "storages.backends.s3.S3Storage"},
})""",
        namespace,
    )

    storages = namespace["STORAGES"]
    assert "default" in storages
    assert storages["default"]["BACKEND"] == "storages.backends.s3.S3Storage"
    assert storages["staticfiles"]["BACKEND"] == "storages.backends.s3.S3Storage"


def test_exec_s3_alone_still_has_both_keys(temp_dir):
    """Simulate base + S3 exec — default and staticfiles both present."""
    namespace = {}
    exec(
        """STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}""",
        namespace,
    )
    exec(
        """STORAGES.update({
    "default": {"BACKEND": "storages.backends.s3.S3Storage", "OPTIONS": {}},
    "staticfiles": {"BACKEND": "storages.backends.s3.S3Storage"},
})""",
        namespace,
    )

    assert "default" in namespace["STORAGES"]
    assert "staticfiles" in namespace["STORAGES"]
    assert (
        namespace["STORAGES"]["default"]["BACKEND"] == "storages.backends.s3.S3Storage"
    )


def test_exec_template_rendered_files_are_syntactically_valid(temp_dir):
    """Verify the template-rendered settings files are valid Python syntax."""
    template_files = [
        Path(__file__).parent
        / "data"
        / "whitenoise"
        / "settings"
        / "packages"
        / "whitenoise.py",
        Path(__file__).parent
        / "data"
        / "django_storages"
        / "s3"
        / "settings"
        / "packages"
        / "django_storages_s3.py",
        Path(__file__).parent
        / "data"
        / "django_storages"
        / "azure"
        / "settings"
        / "packages"
        / "django_storages_azure.py",
        Path(__file__).parent
        / "data"
        / "django_storages"
        / "google"
        / "settings"
        / "packages"
        / "django_storages_google.py",
    ]
    for file_path in template_files:
        try:
            compile(file_path.read_text(), str(file_path), "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {file_path}: {e}")
