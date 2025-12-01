from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-filter
    """
    pm = DjangoProjectManager()

    console.step("Installing django-filter package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-filter")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django-filter"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("django-filter is installed successfully.")


@app.command()
def remove():
    """
    Remove django-filter package
    """
    console.step("Removing django-filter package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("django-filter"):
        uv_runner = UvRunner()
        uv_runner.remove_package("django-filter")

    url_path = Path.joinpath(pm.packages_urls_path, "django_filter.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_filter.py")
    settings_url.unlink(missing_ok=True)

    console.success("django-filter is removed successfully.")
