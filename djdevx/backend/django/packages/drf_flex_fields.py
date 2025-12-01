from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure drf-flex-fields
    """
    pm = DjangoProjectManager()

    console.step("Installing drf-flex-fields package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("drf-flex-fields")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "drf-flex-fields"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("drf-flex-fields is installed successfully.")


@app.command()
def remove():
    """
    Remove drf-flex-fields package
    """
    console.step("Removing drf-flex-fields package ...")

    pm = DjangoProjectManager()
    uv_runner = UvRunner()
    if pm.has_dependency("drf-flex-fields"):
        uv_runner.remove_package("drf-flex-fields")

    url_path = Path.joinpath(pm.packages_urls_path, "drf_flex_fields.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "drf_flex_fields.py")
    settings_url.unlink(missing_ok=True)

    console.success("drf-flex-fields is removed successfully.")
