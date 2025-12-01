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
            help="The Mailgun API key for authentication",
            prompt="Please enter the Mailgun API key for authentication",
            hide_input=True,
        ),
    ],
    domain: Annotated[
        str,
        typer.Option(
            help="The Mailgun domain",
            prompt="Please enter the Mailgun domain",
        ),
    ],
    is_europe: Annotated[
        bool,
        typer.Option(
            help="Flag to use Europe region for Mailgun",
        ),
    ] = False,
):
    """
    Install django-anymail with Mailgun backend
    """
    pm = DjangoProjectManager()

    console.step("Installing django-anymail with Mailgun backend ...")

    uv = UvRunner()
    uv.add_package("django-anymail")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_anymail"
        / "mailgun"
    )

    pm.copy_templates(
        source_dir=source_dir,
        template_context={
            "is_europe": is_europe,
        },
    )

    # Set environment variables
    pm.add_env_variable(key="ANYMAIL_MAILGUN_API_KEY", value=api_key)
    pm.add_env_variable(key="ANYMAIL_MAILGUN_SENDER_DOMAIN", value=domain)

    console.success("django-anymail with Mailgun backend is installed successfully.")


@app.command()
def remove():
    """
    Remove django-anymail Mailgun backend
    """
    pm = DjangoProjectManager()

    console.step("Removing django-anymail package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-anymail"):
        uv.remove_package("django-anymail")

    settings_path = Path.joinpath(
        pm.packages_settings_path, "django_anymail_mailgun.py"
    )
    settings_path.unlink(missing_ok=True)

    pm.remove_env_variable("ANYMAIL_MAILGUN_API_KEY")
    pm.remove_env_variable("ANYMAIL_MAILGUN_SENDER_DOMAIN")

    console.success("django-anymail Mailgun backend is removed successfully.")


@app.command()
def env(
    api_key: Annotated[
        str,
        typer.Option(
            help="The Mailgun API key for authentication",
            prompt="Please enter the Mailgun API key for authentication",
            hide_input=True,
        ),
    ],
    domain: Annotated[
        str,
        typer.Option(
            help="The Mailgun domain",
            prompt="Please enter the Mailgun domain",
        ),
    ],
):
    """
    Configure environment variables for django-anymail Mailgun backend
    """
    pm = DjangoProjectManager()

    console.step(
        "Configuring environment variables for django-anymail Mailgun backend ..."
    )

    pm.add_env_variable(key="ANYMAIL_MAILGUN_API_KEY", value=api_key)
    pm.add_env_variable(key="ANYMAIL_MAILGUN_SENDER_DOMAIN", value=domain)

    console.success(
        "django-anymail Mailgun environment variables are configured successfully."
    )
