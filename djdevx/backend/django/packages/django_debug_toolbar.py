import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-debug-toolbar
    """
    pm = DjangoProjectManager()

    console.step("Installing django-debug-toolbar package ...")

    uv = UvRunner()
    uv.add_package("django-debug-toolbar", group="dev")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "django_debug_toolbar"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-debug-toolbar is installed successfully.")


@app.command()
def remove():
    """
    Remove django-debug-toolbar
    """
    pm = DjangoProjectManager()
    console.step("Removing django-debug-toolbar package ...")

    uv = UvRunner()
    if pm.has_dependency("django-debug-toolbar", "dev"):
        uv.remove_package("django-debug-toolbar", group="dev")

    url_path = Path.joinpath(pm.packages_urls_path, "django_debug_toolbar.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_debug_toolbar.py")
    settings_url.unlink(missing_ok=True)

    console.success("django-debug-toolbar is removed successfully.")
