import subprocess
import typer

from pathlib import Path

from ..utils.print_console import print_step, print_success, print_error, print_info
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
    Install and configure djangochannelsrestframework
    """
    is_project_exists_or_raise()
    if not has_dependency("channels"):
        print_error(
            "'channels' package is a dependency for djangochannelsrestframework. Please install that frist."
        )
        print_info("\n> ddx packages channels install")
        raise typer.Exit(code=1)

    print_step("Installing djangochannelsrestframework package ...")
    subprocess.check_call(["uv", "add", "djangochannelsrestframework"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "djangochannelsrestframework"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("djangochannelsrestframework is installed successfully.")


@app.command()
def remove():
    """
    Remove djangochannelsrestframework package
    """
    print_step("Removing djangochannelsrestframework package ...")
    if has_dependency("djangochannelsrestframework"):
        subprocess.check_call(["uv", "remove", "djangochannelsrestframework"])

    settings_url = Path.joinpath(
        get_packages_settings_path(), "djangochannelsrestframework.py"
    )
    settings_url.unlink(missing_ok=True)

    print_success("djangochannelsrestframework is removed successfully.")
