import typer
from pathlib import Path
from typing_extensions import Annotated

from .....utils.django.uv_runner import UvRunner
from .....utils.print_console import console
from .....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install(
    credentials_file_path: Annotated[
        Path,
        typer.Option(
            help="The path to the google credential file",
            prompt="Please enter the path to the google credential file",
        ),
    ],
    bucket_name: Annotated[
        str,
        typer.Option(
            help="The Google bucket name to store the files in",
            prompt="Please enter the Google bucket name to store the files in",
        ),
    ],
):
    """
    Install django-storages package with Google backend
    """
    pm = DjangoProjectManager()

    console.step("Installing django-storages package with Google backend ...")

    uv = UvRunner()
    uv.add_package("django-storages[google]")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_storages"
        / "google"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    # Set environment variables
    pm.add_env_variable(
        key="STORAGES_GOOGLE_CREDENTIALS", value=str(credentials_file_path)
    )
    pm.add_env_variable(key="STORAGES_GOOGLE_BUCKET_NAME", value=bucket_name)

    console.success("django-storages with Google backend is installed successfully.")


@app.command()
def remove():
    """
    Remove django-storages Google backend
    """
    pm = DjangoProjectManager()

    console.step("Removing django-storages package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-storages"):
        uv.remove_package("django-storages")

    settings_path = Path.joinpath(
        pm.packages_settings_path, "django_storages_google.py"
    )
    settings_path.unlink(missing_ok=True)

    pm.remove_env_variable(key="STORAGES_GOOGLE_CREDENTIALS")
    pm.remove_env_variable(key="STORAGES_GOOGLE_BUCKET_NAME")

    console.success("django-storages Google backend is removed successfully.")


@app.command()
def env(
    credentials_file_path: Annotated[
        Path,
        typer.Option(
            help="The path to the google credential file",
            prompt="Please enter the path to the google credential file",
        ),
    ],
    bucket_name: Annotated[
        str,
        typer.Option(
            help="The Google bucket name to store the files in",
            prompt="Please enter the Google bucket name to store the files in",
        ),
    ],
):
    """
    Configure environment variables for django-storages Google backend
    """
    pm = DjangoProjectManager()

    console.step(
        "Configuring environment variables for django-storages Google backend ..."
    )

    pm.add_env_variable(
        key="STORAGES_GOOGLE_CREDENTIALS", value=str(credentials_file_path)
    )
    pm.add_env_variable(key="STORAGES_GOOGLE_BUCKET_NAME", value=bucket_name)

    console.success(
        "django-storages Google environment variables are configured successfully."
    )
