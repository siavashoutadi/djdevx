from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure drf-spectacular
    """
    pm = DjangoProjectManager()

    print_console.step("Checking if djangorestframework is installed ...")
    if not pm.has_dependency("djangorestframework"):
        print_console.error(
            "'djangorestframework' package is not installed. Please install that package first and try again."
        )
        print_console.info("\n> ddx packages djangorestframework install")
        raise typer.Exit(1)

    print_console.step("Installing drf-spectacular package ...")

    uv_runner = UvRunner()
    uv_runner.add_package("drf-spectacular[sidecar]")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "drf-spectacular"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    print_console.success("drf-spectacular is installed successfully.")


@app.command()
def remove():
    """
    Remove drf-spectacular package
    """
    print_console.step("Removing drf-spectacular package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("drf-spectacular"):
        uv_runner = UvRunner()
        uv_runner.remove_package("drf-spectacular")

    url_path = Path.joinpath(pm.packages_urls_path, "drf_spectacular.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "drf_spectacular.py")
    settings_url.unlink(missing_ok=True)

    print_console.success("drf-spectacular is removed successfully.")
