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
    bucket_name: Annotated[
        str,
        typer.Option(
            help="The AWS bucket name to store the files in",
            prompt="Please enter the AWS bucket name to store the files in",
        ),
    ],
):
    """
    Install django-storages package with S3 backend
    """
    pm = DjangoProjectManager()

    console.step("Installing django-storages package with S3 backend ...")

    uv = UvRunner()
    uv.add_package("django-storages[s3]")

    current_dir = Path(__file__).resolve().parent
    source_dir = (
        current_dir.parent.parent.parent.parent
        / "templates"
        / "django"
        / "django_storages"
        / "s3"
    )

    pm.copy_templates(source_dir=source_dir, template_context={})

    # Set environment variables
    pm.add_env_variable(key="STORAGES_S3_ACCESS_KEY", value=access_key)
    pm.add_env_variable(key="STORAGES_S3_SECRET_KEY", value=secret_key)
    pm.add_env_variable(key="STORAGES_S3_REGION_NAME", value=region_name)
    pm.add_env_variable(key="STORAGES_S3_BUCKET_NAME", value=bucket_name)

    console.success("django-storages with S3 backend is installed successfully.")


@app.command()
def remove():
    """
    Remove django-storages S3 backend
    """
    pm = DjangoProjectManager()

    console.step("Removing django-storages package ...")

    pm = DjangoProjectManager()
    uv = UvRunner()
    if pm.has_dependency("django-storages"):
        uv.remove_package("django-storages")

    settings_path = Path.joinpath(pm.packages_settings_path, "django_storages_s3.py")
    settings_path.unlink(missing_ok=True)

    pm.remove_env_variable(key="STORAGES_S3_ACCESS_KEY")
    pm.remove_env_variable(key="STORAGES_S3_SECRET_KEY")
    pm.remove_env_variable(key="STORAGES_S3_REGION_NAME")
    pm.remove_env_variable(key="STORAGES_S3_BUCKET_NAME")

    console.success("django-storages S3 backend is removed successfully.")


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
    bucket_name: Annotated[
        str,
        typer.Option(
            help="The AWS bucket name to store the files in",
            prompt="Please enter the AWS bucket name to store the files in",
        ),
    ],
):
    """
    Configure environment variables for django-storages S3 backend
    """
    pm = DjangoProjectManager()

    console.step("Configuring environment variables for django-storages S3 backend ...")

    pm.add_env_variable(key="STORAGES_S3_ACCESS_KEY", value=access_key)
    pm.add_env_variable(key="STORAGES_S3_SECRET_KEY", value=secret_key)
    pm.add_env_variable(key="STORAGES_S3_REGION_NAME", value=region_name)
    pm.add_env_variable(key="STORAGES_S3_BUCKET_NAME", value=bucket_name)

    console.success(
        "django-storages S3 environment variables are configured successfully."
    )
