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
    Install and configure django-oauth-toolkit
    """
    is_project_exists_or_raise()

    print_step("Installing django-oauth-toolkit package ...")
    subprocess.check_call(["uv", "add", "django-oauth-toolkit"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "django-oauth-toolkit"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("django-oauth-toolkit is installed successfully.")


@app.command()
def remove():
    """
    Remove django-oauth-toolkit
    """
    print_step("Removing django-oauth-toolkit package ...")
    if has_dependency("django-oauth-toolkit"):
        subprocess.check_call(["uv", "remove", "django-oauth-toolkit"])

    url_path = Path.joinpath(get_packages_url_path(), "django_oauth_toolkit.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(
        get_packages_settings_path(), "django_oauth_toolkit.py"
    )
    settings_url.unlink(missing_ok=True)

    print_success("django-oauth-toolkit is removed successfully.")
