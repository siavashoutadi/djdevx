from ....utils.django.uv_runner import UvRunner
import typer

from pathlib import Path

from ....utils.print_console import console
from ....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def env():
    """
    Creating environment variables for django-defender
    """
    pm = DjangoProjectManager()

    console.step("Creating environment variables for django-defender ...")
    pm.add_env_variable(
        key="DEFENDER_REDIS_URL",
        value="redis://default:${REDIS_PASSWORD}@cache:6379/1",
    )

    console.success(
        "django-defender environment variables are configured successfully."
    )


@app.command()
def install():
    """
    Install and configure django-defender
    """
    pm = DjangoProjectManager()

    console.step("Installing django-defender package ...")
    uv_runner = UvRunner()
    uv_runner.add_package("django-defender")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent / "templates" / "django" / "django-defender"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    env()

    console.success("django-defender is installed successfully.")


@app.command()
def remove():
    """
    Remove django-defender package
    """
    console.step("Removing django-defender package ...")

    pm = DjangoProjectManager()
    if pm.has_dependency("django-defender"):
        uv_runner = UvRunner()
        uv_runner.remove_package("django-defender")

    url_path = Path.joinpath(pm.packages_urls_path, "django_defender.py")
    url_path.unlink(missing_ok=True)

    settings_url = Path.joinpath(pm.packages_settings_path, "django_defender.py")
    settings_url.unlink(missing_ok=True)

    pm.remove_env_variable("DEFENDER_REDIS_URL")

    console.success("django-defender is removed successfully.")
