from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """
    Install and configure django-guardian
    """
    pm = DjangoProjectManager()

    console.step("Installing django-guardian package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-guardian")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django-guardian"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    project_dir = pm.project_path
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

    console.success("django-guardian is installed successfully.")


@app.command()
def remove():
    """
    Remove django-guardian
    """
    console.step("Removing django-guardian package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("django-guardian"):
        uv_runner = UvRunner()
        uv_runner.remove_package("django-guardian")

    project_dir = pm.project_path
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

    url_path = Path.joinpath(pm.packages_urls_path, "django_guardian.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_guardian.py")
    settings_url.unlink(missing_ok=True)

    console.success("django-guardian is removed successfully.")
