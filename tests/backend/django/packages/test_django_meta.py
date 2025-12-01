from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-meta"


def test_django_meta_install_and_remove(temp_dir):
    """
    Test django-meta package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Run install with all the parameters to match our test data
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-meta",
            "install",
            "--site-protocol",
            "https",
            "--site-domain",
            "example.com",
            "--site-name",
            "Test Site",
            "--site-type",
            "website",
            "--use-og-properties",
            "--use-twitter-properties",
            "--use-schemaorg-properties",
            "--use-title-tag",
            "--configure-facebook",
            "--fb-app-id",
            "123456",
            "--fb-pages",
            "789012",
            "--fb-publisher",
            "https://facebook.com/testpage",
            "--configure-twitter",
            "--twitter-site",
            "@testsite",
            "--twitter-author",
            "@testauthor",
            "--twitter-type",
            "summary_large_image",
            "--default-image-url",
            "https://example.com/image.jpg",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = backend_dir / "settings" / "packages" / "django_meta.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "django_meta.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    assert DjangoProjectManager().has_dependency("django-meta"), (
        "Django-meta dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-meta",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"

    assert not DjangoProjectManager().has_dependency("django-meta"), (
        "Django-meta dependency found after removal"
    )
