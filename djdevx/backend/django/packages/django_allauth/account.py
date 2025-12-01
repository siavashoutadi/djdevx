import typer
import shutil
from pathlib import Path
from typing_extensions import Annotated

from .....utils.django.uv_runner import UvRunner
from .....utils.print_console import console
from .....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install(
    email_subject_prefix: Annotated[
        str,
        typer.Option(
            help="Subject-line prefix to use for email messages sent",
            prompt="Please enter the Subject-line prefix to use for email messages sent. e.g. '[example.com] - '",
        ),
    ] = "",
    is_profanity_for_username_enabled: Annotated[
        bool,
        typer.Option(
            help="Enable profanity filter for username",
            prompt="Enable profanity filter for username",
        ),
    ] = True,
    account_url_prefix: Annotated[
        str,
        typer.Option(
            help="URL prefix for account related URLs",
            prompt="Please enter the URL prefix for account related URLs",
        ),
    ] = "auth",
):
    """
    Install django-allauth package with account functionality
    """
    pm = DjangoProjectManager()

    console.step("Installing django-allauth package with account functionality ...")

    uv = UvRunner()
    uv.add_package("django-allauth")
    if is_profanity_for_username_enabled:
        uv.add_package("better-profanity")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_allauth"
        / "account"
    )

    pm.copy_templates(
        source_dir=source_dir,
        template_context={
            "email_subject_prefix": email_subject_prefix,
            "is_profanity_for_username_enabled": is_profanity_for_username_enabled,
            "account_url_prefix": account_url_prefix,
        },
    )

    console.success(
        "django-allauth with account functionality is installed successfully."
    )


@app.command()
def remove():
    """
    Remove django-allauth account functionality
    """
    pm = DjangoProjectManager()

    console.step("Removing django-allauth package ...")

    settings_path = Path.joinpath(
        pm.packages_settings_path, "django_allauth_account.py"
    )
    settings_path.unlink(missing_ok=True)

    url_path = Path.joinpath(pm.urls_path, "django_allauth_account.py")
    url_path.unlink(missing_ok=True)

    authentication_path = Path.joinpath(pm.project_path, "authentication")
    shutil.rmtree(authentication_path, ignore_errors=True)

    css_path = Path.joinpath(pm.project_path, "static", "css", "vendor", "auth.css")
    css_path.unlink(missing_ok=True)

    uv = UvRunner()
    for dep in ["django-allauth", "better-profanity"]:
        if pm.has_dependency(dep):
            uv.remove_package(dep)

    console.success("django-allauth account functionality is removed successfully.")


@app.command()
def env():
    """
    Configure environment variables for django-allauth
    """
    console.step(
        "No additional environment variables needed for django-allauth account functionality"
    )
    console.success("django-allauth account functionality uses Django settings only.")
