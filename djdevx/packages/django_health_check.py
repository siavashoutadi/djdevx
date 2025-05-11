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
    Install and configure django-health-check
    """
    is_project_exists_or_raise()

    print_step("Installing django-health-check package ...")
    subprocess.check_call(["uv", "add", "django-health-check", "psutil"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "django_health_check"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    print_success("django-health-check is installed successfully.")


@app.command()
def remove():
    """
    Remove django-health-check
    """
    print_step("Removing django-health-check package ...")
    for dep in ["django-health-check", "psutil"]:
        if has_dependency(dep):
            subprocess.check_call(["uv", "remove", dep])

    url_path = Path.joinpath(get_packages_url_path(), "django_health_check.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(get_packages_settings_path(), "django_health_check.py")
    settings_url.unlink(missing_ok=True)

    print_success("django-health-check is removed successfully.")
