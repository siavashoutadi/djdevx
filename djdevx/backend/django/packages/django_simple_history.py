from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-simple-history
    """
    pm = DjangoProjectManager()

    print_console.step("Installing django-simple-history package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-simple-history")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent
        / "templates"
        / "django"
        / "django-simple-history"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    print_console.success("django-simple-history is installed successfully.")


@app.command()
def remove():
    """
    Remove django-simple-history package
    """
    print_console.step("Removing django-simple-history package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("django-simple-history"):
        uv_runner = UvRunner()
        uv_runner.remove_package("django-simple-history")

    url_path = Path.joinpath(pm.packages_urls_path, "django_simple_history.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_simple_history.py")
    settings_url.unlink(missing_ok=True)

    print_console.success("django-simple-history is removed successfully.")
