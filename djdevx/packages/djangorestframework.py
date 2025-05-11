import subprocess
import typer

from pathlib import Path

from ..utils.print_console import print_step, print_success
from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
    get_packages_url_path,
    get_packages_settings_path,
)
from ..utils.project_info import has_dependency

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure djangorestframework
    """
    is_project_exists_or_raise()

    print_step("Installing djangorestframework package ...")
    subprocess.check_call(["uv", "add", "djangorestframework"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "djangorestframework"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("djangorestframework is installed successfully.")


@app.command()
def remove():
    """
    Remove djangorestframework
    """
    print_step("Removing djangorestframework package ...")
    if has_dependency("djangorestframework"):
        subprocess.check_call(["uv", "remove", "djangorestframework"])

    url_path = Path.joinpath(get_packages_url_path(), "djangorestframework.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(get_packages_settings_path(), "djangorestframework.py")
    settings_url.unlink(missing_ok=True)

    print_success("djangorestframework is removed successfully.")
