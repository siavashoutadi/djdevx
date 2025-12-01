from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure heroicons
    """
    pm = DjangoProjectManager()

    console.step("Installing heroicons package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("heroicons[django]")

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent.parent / "templates" / "django" / "heroicons"

    pm.copy_templates(source_dir=source_dir, template_context={})

    console.success("heroicons is installed successfully.")


@app.command()
def remove():
    """
    Remove heroicons
    """
    console.step("Removing heroicons package ...")

    pm = DjangoProjectManager()
    uv_runner = UvRunner()
    if pm.has_dependency("heroicons"):
        uv_runner.remove_package("heroicons")

    settings_path = Path.joinpath(pm.packages_settings_path, "heroicons.py")
    settings_path.unlink(missing_ok=True)

    console.success("heroicons is removed successfully.")
