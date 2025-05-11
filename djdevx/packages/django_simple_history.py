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
    Install and configure django-simple-history
    """
    is_project_exists_or_raise()

    print_step("Installing django-simple-history package ...")
    subprocess.check_call(["uv", "add", "django-simple-history"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "django-simple-history"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("django-simple-history is installed successfully.")


@app.command()
def remove():
    """
    Remove django-simple-history package
    """
    print_step("Removing django-simple-history package ...")
    if has_dependency("django-simple-history"):
        subprocess.check_call(["uv", "remove", "django-simple-history"])

    url_path = Path.joinpath(get_packages_url_path(), "django_simple_history.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(
        get_packages_settings_path(), "django_simple_history.py"
    )
    settings_url.unlink(missing_ok=True)

    print_success("django-simple-history is removed successfully.")
