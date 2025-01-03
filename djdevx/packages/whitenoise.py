import subprocess
import typer

from pathlib import Path

from ..utils.print_console import print_step, print_success
from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
    get_packages_settings_path,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure whitenoise
    """
    is_project_exists_or_raise()

    print_step("Installing whitenoise package ...")
    subprocess.check_call(["uv", "add", "whitenoise"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent / "templates" / "whitenoise"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("whitenoise is installed successfully.")


@app.command()
def remove():
    """
    Remove whitenoise
    """
    print_step("Removing whitenoise package ...")
    subprocess.check_call(["uv", "remove", "whitenoise"])

    settings_url = Path.joinpath(get_packages_settings_path(), "whitenoise.py")
    settings_url.unlink(missing_ok=True)

    print_success("whitenoise is removed successfully.")
