import typer
from pathlib import Path
from typing_extensions import Annotated

from .....utils.django.uv_runner import UvRunner
from .....utils.print_console import console
from .....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install(
    access_key: Annotated[
        str,
        typer.Option(
            help="The AWS access key for authentication",
            prompt="Please enter the AWS access key for authentication",
        ),
    ],
    secret_key: Annotated[
        str,
        typer.Option(
            help="The AWS Secret key for authentication",
            prompt="Please enter the AWS secret key for authentication",
            hide_input=True,
        ),
    ],
    region_name: Annotated[
        str,
        typer.Option(
            help="The AWS region",
            prompt="Please enter the AWS region",
        ),
    ],
):
    """
    Install django-anymail with SES backend
    """
    pm = DjangoProjectManager()

    console.step("Installing django-anymail with SES backend ...")

    uv = UvRunner()
    uv.add_package("django-anymail[amazon-ses]")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_anymail"
        / "ses"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    # Set environment variables
    pm.add_env_variable(key="ANYMAIL_SES_ACCESS_KEY", value=access_key)
    pm.add_env_variable(key="ANYMAIL_SES_SECRET_KEY", value=secret_key)
    pm.add_env_variable(key="ANYMAIL_SES_REGION_NAME", value=region_name)

    console.success("django-anymail with SES backend is installed successfully.")


@app.command()
def remove():
    """
    Remove django-anymail SES backend
    """
    pm = DjangoProjectManager()

    console.step("Removing django-anymail package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-anymail"):
        uv.remove_package("django-anymail")

    settings_path = Path.joinpath(pm.packages_settings_path, "django_anymail_ses.py")
    settings_path.unlink(missing_ok=True)

    pm.remove_env_variable("ANYMAIL_SES_ACCESS_KEY")
    pm.remove_env_variable("ANYMAIL_SES_SECRET_KEY")
    pm.remove_env_variable("ANYMAIL_SES_REGION_NAME")

    console.success("django-anymail SES backend is removed successfully.")


@app.command()
def env(
    access_key: Annotated[
        str,
        typer.Option(
            help="The AWS access key for authentication",
            prompt="Please enter the AWS access key for authentication",
        ),
    ],
    secret_key: Annotated[
        str,
        typer.Option(
            help="The AWS Secret key for authentication",
            prompt="Please enter the AWS secret key for authentication",
            hide_input=True,
        ),
    ],
    region_name: Annotated[
        str,
        typer.Option(
            help="The AWS region",
            prompt="Please enter the AWS region",
        ),
    ],
):
    """
    Configure environment variables for django-anymail SES backend
    """
    pm = DjangoProjectManager()

    console.step("Configuring environment variables for django-anymail SES backend ...")

    pm.add_env_variable(key="ANYMAIL_SES_ACCESS_KEY", value=access_key)
    pm.add_env_variable(key="ANYMAIL_SES_SECRET_KEY", value=secret_key)
    pm.add_env_variable(key="ANYMAIL_SES_REGION_NAME", value=region_name)

    console.success(
        "django-anymail SES environment variables are configured successfully."
    )
