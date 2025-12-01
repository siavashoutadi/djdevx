import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-cors-headers
    """
    pm = DjangoProjectManager()

    console.step("Installing django-cors-headers package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-cors-headers")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "django-cors-headers"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-cors-headers is installed successfully.")


@app.command()
def remove():
    """
    Remove django-cors-headers package
    """
    console.step("Removing django-cors-headers package ...")
    pm = DjangoProjectManager()
    if pm.has_dependency("django-cors-headers"):
        uv_runner = UvRunner()
        uv_runner.remove_package("django-cors-headers")

    url_path = Path.joinpath(pm.packages_urls_path, "django_cors_headers.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_cors_headers.py")
    settings_url.unlink(missing_ok=True)

    console.success("django-cors-headers is removed successfully.")
