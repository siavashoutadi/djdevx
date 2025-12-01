import typer
from pathlib import Path
from typing_extensions import Annotated

from .....utils.django.uv_runner import UvRunner
from .....utils.print_console import console
from .....utils.django.project_manager import DjangoProjectManager

app = typer.Typer(no_args_is_help=True)


@app.command()
def install(
    account_key: Annotated[
        str,
        typer.Option(
            help="The Azure account key for authentication",
            prompt="Please enter the Azure account key for authentication",
        ),
    ],
    account_name: Annotated[
        str,
        typer.Option(
            help="The Azure account name for authentication",
            prompt="Please enter the Azure account name for authentication",
        ),
    ],
    container_name: Annotated[
        str,
        typer.Option(
            help="The Azure container name to store the files in",
            prompt="Please enter the Azure container name to store the files in",
        ),
    ],
):
    """
    Install django-storages package with Azure backend
    """
    pm = DjangoProjectManager()

    console.step("Installing django-storages package with Azure backend ...")

    uv = UvRunner()
    uv.add_package("django-storages[azure]")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_storages"
        / "azure"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    # Set environment variables
    pm.add_env_variable(key="STORAGES_AZURE_ACCOUNT_KEY", value=account_key)
    pm.add_env_variable(key="STORAGES_AZURE_ACCOUNT_NAME", value=account_name)
    pm.add_env_variable(key="STORAGES_AZURE_CONTAINER_NAME", value=container_name)

    console.success("django-storages with Azure backend is installed successfully.")


@app.command()
def remove():
    """
    Remove django-storages Azure backend
    """
    pm = DjangoProjectManager()

    console.step("Removing django-storages package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-storages"):
        uv.remove_package("django-storages")

    settings_path = Path.joinpath(pm.packages_settings_path, "django_storages_azure.py")
    settings_path.unlink(missing_ok=True)

    pm.remove_env_variable(key="STORAGES_AZURE_ACCOUNT_KEY")
    pm.remove_env_variable(key="STORAGES_AZURE_ACCOUNT_NAME")
    pm.remove_env_variable(key="STORAGES_AZURE_CONTAINER_NAME")

    console.success("django-storages Azure backend is removed successfully.")


@app.command()
def env(
    account_key: Annotated[
        str,
        typer.Option(
            help="The Azure account key for authentication",
            prompt="Please enter the Azure account key for authentication",
        ),
    ],
    account_name: Annotated[
        str,
        typer.Option(
            help="The Azure account name for authentication",
            prompt="Please enter the Azure account name for authentication",
        ),
    ],
    container_name: Annotated[
        str,
        typer.Option(
            help="The Azure container name to store the files in",
            prompt="Please enter the Azure container name to store the files in",
        ),
    ],
):
    """
    Configure environment variables for django-storages Azure backend
    """
    pm = DjangoProjectManager()

    console.step(
        "Configuring environment variables for django-storages Azure backend ..."
    )

    pm.add_env_variable(key="STORAGES_AZURE_ACCOUNT_KEY", value=account_key)
    pm.add_env_variable(key="STORAGES_AZURE_ACCOUNT_NAME", value=account_name)
    pm.add_env_variable(key="STORAGES_AZURE_CONTAINER_NAME", value=container_name)

    console.success(
        "django-storages Azure environment variables are configured successfully."
    )
