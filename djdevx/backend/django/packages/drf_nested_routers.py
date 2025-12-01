from ....utils.django.uv_runner import UvRunner
import typer

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure drf-nested-routers
    """
    console.step("Installing drf-nested-routers package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("drf-nested-routers")

    console.success("drf-nested-routers is installed successfully.")


@app.command()
def remove():
    """
    Remove drf-nested-routers package
    """
    console.step("Removing drf-nested-routers package ...")

    pm = DjangoProjectManager()
    uv_runner = UvRunner()
    if pm.has_dependency("drf-nested-routers"):
        uv_runner.remove_package("drf-nested-routers")

    console.success("drf-nested-routers is removed successfully.")
