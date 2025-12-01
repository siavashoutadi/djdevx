from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure drf-spectacular
    """
    pm = DjangoProjectManager()

    console.step("Checking if djangorestframework is installed ...")
    if not pm.has_dependency("djangorestframework"):
        console.error(
            "'djangorestframework' package is not installed. Please install that package first and try again."
        )
        console.info("\n> ddx packages djangorestframework install")
        raise typer.Exit(1)

    console.step("Installing drf-spectacular package ...")

    uv_runner = UvRunner()
    uv_runner.add_package("drf-spectacular[sidecar]")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "drf-spectacular"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("drf-spectacular is installed successfully.")


@app.command()
def remove():
    """
    Remove drf-spectacular package
    """
    console.step("Removing drf-spectacular package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("drf-spectacular"):
        uv_runner = UvRunner()
        uv_runner.remove_package("drf-spectacular")

    url_path = Path.joinpath(pm.packages_urls_path, "drf_spectacular.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "drf_spectacular.py")
    settings_url.unlink(missing_ok=True)

    console.success("drf-spectacular is removed successfully.")
