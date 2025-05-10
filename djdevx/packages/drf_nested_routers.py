import subprocess
import typer

from ..utils.print_console import print_step, print_success
from ..utils.project_info import has_dependency
from ..utils.project_files import is_project_exists_or_raise


app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure drf-nested-routers
    """
    is_project_exists_or_raise()

    print_step("Installing drf-nested-routers package ...")
    subprocess.check_call(["uv", "add", "drf-nested-routers"])

    print_success("drf-nested-routers is installed successfully.")


@app.command()
def remove():
    """
    Remove drf-nested-routers package
    """
    print_step("Removing drf-nested-routers package ...")
    if has_dependency("drf-nested-routers"):
        subprocess.check_call(["uv", "remove", "drf-nested-routers"])

    print_success("drf-nested-routers is removed successfully.")
