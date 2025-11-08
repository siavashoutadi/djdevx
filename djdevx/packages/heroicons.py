import subprocess
import typer

from pathlib import Path

from ..utils.print_console import print_step, print_success
from ..utils.project_info import has_dependency
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
    Install and configure heroicons
    """
    is_project_exists_or_raise()

    print_step("Installing heroicons package ...")
    subprocess.check_call(["uv", "add", "heroicons[django]"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "heroicons"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("heroicons is installed successfully.")


@app.command()
def remove():
    """
    Remove heroicons
    """
    print_step("Removing heroicons package ...")

    if has_dependency("heroicons"):
        subprocess.check_call(["uv", "remove", "heroicons"])

    settings_path = Path.joinpath(get_packages_settings_path(), "heroicons.py")
    settings_path.unlink(missing_ok=True)

    print_success("heroicons is removed successfully.")
