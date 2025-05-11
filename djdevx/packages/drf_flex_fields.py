import subprocess
import typer

from pathlib import Path

from ..utils.print_console import print_step, print_success
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
    Install and configure drf-flex-fields
    """
    is_project_exists_or_raise()

    print_step("Installing drf-flex-fields package ...")
    subprocess.check_call(["uv", "add", "drf-flex-fields"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent / "templates" / "drf-flex-fields"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("drf-flex-fields is installed successfully.")


@app.command()
def remove():
    """
    Remove drf-flex-fields package
    """
    print_step("Removing drf-flex-fields package ...")
    if has_dependency("drf-flex-fields"):
        subprocess.check_call(["uv", "remove", "drf-flex-fields"])

    url_path = Path.joinpath(get_packages_url_path(), "drf_flex_fields.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(get_packages_settings_path(), "drf_flex_fields.py")
    settings_url.unlink(missing_ok=True)

    print_success("drf-flex-fields is removed successfully.")
