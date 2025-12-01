import typer
from pathlib import Path
from typing_extensions import Annotated

from .....utils.django.uv_runner import UvRunner
from .....utils.print_console import console
from .....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install(
    api_key: Annotated[
        str,
        typer.Option(
            help="The Resend API key for authentication",
            prompt="Please enter the Resend API key for authentication",
            hide_input=True,
        ),
    ],
):
    """
    Install django-anymail with Resend backend
    """
    pm = DjangoProjectManager()

    console.step("Installing django-anymail with Resend backend ...")

    uv = UvRunner()
    uv.add_package("django-anymail")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_anymail"
        / "resend"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    # Set environment variables
    pm.add_env_variable(key="ANYMAIL_RESEND_API_KEY", value=api_key)

    console.success("django-anymail with Resend backend is installed successfully.")


@app.command()
def remove():
    """
    Remove django-anymail Resend backend
    """
    pm = DjangoProjectManager()

    console.step("Removing django-anymail package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-anymail"):
        uv.remove_package("django-anymail")

    settings_path = Path.joinpath(pm.packages_settings_path, "django_anymail_resend.py")
    settings_path.unlink(missing_ok=True)

    pm.remove_env_variable("ANYMAIL_RESEND_API_KEY")

    console.success("django-anymail Resend backend is removed successfully.")


@app.command()
def env(
    api_key: Annotated[
        str,
        typer.Option(
            help="The Resend API key for authentication",
            prompt="Please enter the Resend API key for authentication",
            hide_input=True,
        ),
    ],
):
    """
    Configure environment variables for django-anymail Resend backend
    """
    pm = DjangoProjectManager()

    console.step(
        "Configuring environment variables for django-anymail Resend backend ..."
    )

    pm.add_env_variable(key="ANYMAIL_RESEND_API_KEY", value=api_key)

    console.success(
        "django-anymail Resend environment variables are configured successfully."
    )
