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
    add_env_varibles,
    remove_env_varibles,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def env():
    """
    Creating environment variables for django-defender
    """
    is_project_exists_or_raise()

    print_step("Creating environment variables for django-defender ...")
    add_env_varibles(
        key="DEFENDER_REDIS_URL",
        value="redis://default:${REDIS_PASSWORD}@cache:6379/1",
    )

    print_success("django-defender environment variables are configured successfully.")


@app.command()
def install():
    """
    Install and configure django-defender
    """
    is_project_exists_or_raise()

    print_step("Installing django-defender package ...")
    subprocess.check_call(["uv", "add", "django-defender"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent / "templates" / "django-defender"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    env()

    print_success("django-defender is installed successfully.")


@app.command()
def remove():
    """
    Remove django-defender package
    """
    print_step("Removing django-defender package ...")
    if has_dependency("django-defender"):
        subprocess.check_call(["uv", "remove", "django-defender"])

    url_path = Path.joinpath(get_packages_url_path(), "django_defender.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(get_packages_settings_path(), "django_defender.py")
    settings_url.unlink(missing_ok=True)

    remove_env_varibles("DEFENDER_REDIS_URL")

    print_success("django-defender is removed successfully.")
