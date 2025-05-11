import subprocess
import typer

from pathlib import Path

from ..utils.print_console import print_step, print_success, print_error, print_info
from ..utils.project_info import has_dependency
from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
    get_packages_url_path,
    get_packages_settings_path,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure drf-spectacular
    """
    is_project_exists_or_raise()

    print_step("Checking if djangorestframework is installed ...")
    if not has_dependency("djangorestframework"):
        print_error(
            "'djangorestframework' package is not installed. Please install that package first and try again."
        )
        print_info("\n> ddx packages djangorestframework install")
        raise typer.Exit(1)

    print_step("Installing drf-spectacular package ...")

    subprocess.check_call(["uv", "add", "drf-spectacular[sidecar]"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "drf-spectacular"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("drf-spectacular is installed successfully.")


@app.command()
def remove():
    """
    Remove drf-spectacular package
    """
    print_step("Removing drf-spectacular package ...")
    if has_dependency("drf-spectacular"):
        subprocess.check_call(["uv", "remove", "drf-spectacular"])

    url_path = Path.joinpath(get_packages_url_path(), "drf_spectacular.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(get_packages_settings_path(), "drf_spectacular.py")
    settings_url.unlink(missing_ok=True)

    print_success("drf-spectacular is removed successfully.")
