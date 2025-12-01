from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-snakeoil"


def test_django_snakeoil_install_and_remove(temp_dir):
    """
    Test django-snakeoil package installation and removal.
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
            "django-snakeoil",
            "install",
            "--site-name",
            "Test Site",
            "--site-description",
            "Test site description",
            "--author",
            "Test Author",
            "--og-type",
            "website",
            "--default-image-url",
            "https://example.com/image.jpg",
            "--site-url",
            "https://example.com",
            "--locale",
            "en_US",
            "--twitter-site",
            "@testsite",
            "--twitter-card-type",
            "summary_large_image",
            "--keywords",
            "test, django, seo",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = backend_dir / "settings" / "packages" / "django_snakeoil.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "django_snakeoil.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    assert DjangoProjectManager().has_dependency("django-snakeoil"), (
        "django-snakeoil dependency not found after installation"
    )

    # Check that base template was modified (this package modifies templates)
    base_template_path = backend_dir / "templates" / "base.html"
    if base_template_path.exists():
        base_content = base_template_path.read_text()
        assert "{% load snakeoil %}" in base_content, (
            "Snakeoil template tag not added to base template"
        )
        assert "{% meta %}" in base_content, (
            "Meta template tag not added to base template"
        )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-snakeoil",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"

    assert not DjangoProjectManager().has_dependency("django-snakeoil"), (
        "django-snakeoil dependency found after removal"
    )

    # Check that base template modifications were removed
    if base_template_path.exists():
        base_content = base_template_path.read_text()
        assert "{% load snakeoil %}" not in base_content, (
            "Snakeoil template tag not removed from base template"
        )
        assert "{% meta %}" not in base_content, (
            "Meta template tag not removed from base template"
        )
