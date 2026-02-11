import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


def add_htmx_snippets():
    """Add HTMX script and CSRF headers to base template."""
    import re

    pm = DjangoProjectManager()
    base_template = pm.base_template_path
    content = base_template.read_text()

    if "{% load django_htmx %}" not in content:
        content = "{% load django_htmx %}\n" + content

    if "{% htmx_script %}" not in content:
        content = content.replace("</head>", "  {% htmx_script %}\n  </head>")

    if "hx-headers=" not in content:
        # Find the opening body tag and add hx-headers attribute while preserving existing attributes
        body_pattern = r"<body([^>]*)>"
        replacement = r'<body\1 hx-headers=\'{"x-csrftoken": "{{ csrf_token }}"}\'>'
        content = re.sub(body_pattern, replacement, content)

    base_template.write_text(content)


def remove_htmx_snippets():
    """Remove HTMX script and CSRF headers from base template."""
    import re

    pm = DjangoProjectManager()
    base_template = pm.base_template_path
    content = base_template.read_text()

    # Remove load tag
    content = content.replace("{% load django_htmx %}\n", "")

    # Remove htmx_script tag
    content = content.replace("  {% htmx_script %}\n", "")

    # Remove hx-headers attribute from body tag while preserving other attributes
    # Pattern handles both regular and escaped quotes
    hx_headers_pattern = (
        r' hx-headers=\\?\'{"x-csrftoken": "{{ csrf_token }}"}\\?\'(?=[\s>])'
    )
    content = re.sub(hx_headers_pattern, "", content)

    base_template.write_text(content)


@app.command()
def install():
    """
    Install and configure django-htmx
    """
    pm = DjangoProjectManager()

    console.step("Installing django-htmx package ...")

    uv = UvRunner()
    uv.add_package("django-htmx")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django_htmx"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    add_htmx_snippets()

    console.success("django-htmx is installed successfully.")


@app.command()
def remove():
    """
    Remove django-htmx
    """
    console.step("Removing django-htmx package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-htmx"):
        uv.remove_package("django-htmx")

    settings_path = Path.joinpath(pm.packages_settings_path, "django_htmx.py")
    settings_path.unlink(missing_ok=True)

    remove_htmx_snippets()

    console.success("django-htmx is removed successfully.")
