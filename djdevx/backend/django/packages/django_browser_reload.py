import typer

from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-browser-reload
    """
    pm = DjangoProjectManager()

    console.step("Installing django-browser-reload package ...")

    uv = UvRunner()
    uv.add_package("django-browser-reload", group="dev")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "django_browser_reload"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-browser-reload is installed successfully.")


@app.command()
def remove():
    """
    Remove django-browser-reload
    """
    console.step("Removing django-browser-reload package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-browser-reload", "dev"):
        uv.remove_package("django-browser-reload", group="dev")

    url_path = Path.joinpath(pm.packages_urls_path, "django_browser_reload.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_browser_reload.py")
    settings_url.unlink(missing_ok=True)

    console.success("django-browser-reload is removed successfully.")
