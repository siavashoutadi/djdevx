from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django-htmx"


def test_django_htmx_install_and_remove(temp_dir):
    """
    Test django-htmx package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-htmx",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = backend_dir / "settings" / "packages" / "django_htmx.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = DATA_DIR / "settings" / "packages" / "django_htmx.py"
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    # Check base template was updated with HTMX snippets
    base_template = backend_dir / "templates" / "_base.html"
    assert base_template.exists(), "Base template not found"

    template_content = base_template.read_text()
    assert "{% load django_htmx %}" in template_content, "HTMX load tag not added"
    assert "{% htmx_script %}" in template_content, "HTMX script tag not added"
    assert "hx-headers=" in template_content and "x-csrftoken" in template_content, (
        "CSRF headers not added"
    )

    assert DjangoProjectManager().has_dependency("django-htmx"), (
        "django-htmx dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-htmx",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"

    # Check base template was cleaned up
    template_content = base_template.read_text()
    assert "{% load django_htmx %}" not in template_content, "HTMX load tag not removed"
    assert "{% htmx_script %}" not in template_content, "HTMX script tag not removed"

    assert not DjangoProjectManager().has_dependency("django-htmx"), (
        "django-htmx dependency not removed after removal"
    )


def test_django_htmx_with_body_class(temp_dir):
    """
    Test django-htmx installation with existing body class attribute.
    """
    from djdevx.backend.django.packages.django_htmx import (
        add_htmx_snippets,
        remove_htmx_snippets,
    )

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Modify the base template to have a class attribute on body
    base_template = backend_dir / "templates" / "_base.html"
    content = base_template.read_text()
    content = content.replace("<body>", '<body class="custom-theme">')
    base_template.write_text(content)

    # Add HTMX snippets
    add_htmx_snippets()

    # Verify hx-headers was added while preserving the class
    template_content = base_template.read_text()
    assert 'class="custom-theme"' in template_content, "Body class attribute was lost"
    assert "hx-headers=" in template_content, "hx-headers attribute was not added"

    # Remove HTMX snippets
    remove_htmx_snippets()

    # Verify hx-headers was removed but class remains
    template_content = base_template.read_text()
    assert 'class="custom-theme"' in template_content, (
        "Body class attribute was lost after removal"
    )
    assert "hx-headers=" not in template_content, "hx-headers attribute was not removed"


def test_django_htmx_with_body_attributes(temp_dir):
    """
    Test django-htmx installation with existing body attributes (id, data-*, etc).
    """
    from djdevx.backend.django.packages.django_htmx import (
        add_htmx_snippets,
        remove_htmx_snippets,
    )

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Modify the base template to have multiple attributes on body
    base_template = backend_dir / "templates" / "_base.html"
    content = base_template.read_text()
    content = content.replace(
        "<body>", '<body id="app" data-theme="dark" data-locale="en">'
    )
    base_template.write_text(content)

    # Add HTMX snippets
    add_htmx_snippets()

    # Verify hx-headers was added while preserving all attributes
    template_content = base_template.read_text()
    assert 'id="app"' in template_content, "id attribute was lost"
    assert 'data-theme="dark"' in template_content, "data-theme attribute was lost"
    assert 'data-locale="en"' in template_content, "data-locale attribute was lost"
    assert "hx-headers=" in template_content, "hx-headers attribute was not added"

    # Remove HTMX snippets
    remove_htmx_snippets()

    # Verify hx-headers was removed but all attributes remain
    template_content = base_template.read_text()
    assert 'id="app"' in template_content, "id attribute was lost after removal"
    assert 'data-theme="dark"' in template_content, (
        "data-theme attribute was lost after removal"
    )
    assert 'data-locale="en"' in template_content, (
        "data-locale attribute was lost after removal"
    )
    assert "hx-headers=" not in template_content, "hx-headers attribute was not removed"


def test_django_htmx_with_complex_body(temp_dir):
    """
    Test django-htmx installation with complex body tag (multiple spaces, newlines, etc).
    """
    from djdevx.backend.django.packages.django_htmx import (
        add_htmx_snippets,
        remove_htmx_snippets,
    )

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # Modify the base template with complex body formatting
    base_template = backend_dir / "templates" / "_base.html"
    content = base_template.read_text()
    content = content.replace(
        "<body>",
        '<body\n    class="main-app"\n    id="root"\n    data-version="1.0"\n  >',
    )
    base_template.write_text(content)

    # Add HTMX snippets
    add_htmx_snippets()

    # Verify hx-headers was added while preserving all formatting and attributes
    template_content = base_template.read_text()
    assert 'class="main-app"' in template_content, "class attribute was lost"
    assert 'id="root"' in template_content, "id attribute was lost"
    assert 'data-version="1.0"' in template_content, "data-version attribute was lost"
    assert "hx-headers=" in template_content, "hx-headers attribute was not added"

    # Remove HTMX snippets
    remove_htmx_snippets()

    # Verify hx-headers was removed but all attributes remain
    template_content = base_template.read_text()
    assert 'class="main-app"' in template_content, (
        "class attribute was lost after removal"
    )
    assert 'id="root"' in template_content, "id attribute was lost after removal"
    assert 'data-version="1.0"' in template_content, (
        "data-version attribute was lost after removal"
    )
    assert "hx-headers=" not in template_content, "hx-headers attribute was not removed"
