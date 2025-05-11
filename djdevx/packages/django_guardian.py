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
    Install and configure django-guardian
    """
    is_project_exists_or_raise()

    print_step("Installing django-guardian package ...")
    subprocess.check_call(["uv", "add", "django-guardian"])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "django-guardian"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context={}
    )

    user_mode_file = project_dir / "users" / "models.py"

    if user_mode_file.exists():
        content = user_mode_file.read_text()
        if "GuardianUserMixin" not in content:
            updated_content = content.replace(
                "from django.contrib.auth.models import AbstractUser",
                "from django.contrib.auth.models import AbstractUser\nfrom guardian.mixins import GuardianUserMixin",
            ).replace(
                "class User(AbstractUser):",
                "class User(AbstractUser, GuardianUserMixin):",
            )
            user_mode_file.write_text(updated_content)

    print_success("django-guardian is installed successfully.")


@app.command()
def remove():
    """
    Remove django-guardian
    """
    print_step("Removing django-guardian package ...")
    if has_dependency("django-guardian"):
        subprocess.check_call(["uv", "remove", "django-guardian"])

    project_dir = get_project_path()
    user_mode_file = project_dir / "users" / "models.py"

    if user_mode_file.exists():
        content = user_mode_file.read_text()
        if "GuardianUserMixin" in content:
            updated_content = (
                "\n".join(
                    line
                    for line in content.splitlines()
                    if "from guardian.mixins import GuardianUserMixin" not in line
                ).replace(
                    "class User(AbstractUser, GuardianUserMixin):",
                    "class User(AbstractUser):",
                )
                + "\n"
            )
            user_mode_file.write_text(updated_content)

    url_path = Path.joinpath(get_packages_url_path(), "django_guardian.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(get_packages_settings_path(), "django_guardian.py")
    settings_url.unlink(missing_ok=True)

    print_success("django-guardian is removed successfully.")
