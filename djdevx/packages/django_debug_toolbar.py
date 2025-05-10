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
    Install and configure django-debug-toolbar
    """
    is_project_exists_or_raise()

    print_step("Installing django-debug-toolbar package ...")
    subprocess.check_call(["uv", "add", "django-debug-toolbar", "--dev"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent / "templates" / "django_debug_toolbar"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("django-debug-toolbar is installed successfully.")


@app.command()
def remove():
    """
    Remove django-debug-toolbar
    """
    print_step("Removing django-debug-toolbar package ...")
    if has_dependency("django-debug-toolbar", "dev"):
        subprocess.check_call(
            ["uv", "remove", "django-debug-toolbar", "--group", "dev"]
        )

    url_path = Path.joinpath(get_packages_url_path(), "django_debug_toolbar.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(
        get_packages_settings_path(), "django_debug_toolbar.py"
    )
    settings_url.unlink(missing_ok=True)

    print_success("django-debug-toolbar is removed successfully.")
