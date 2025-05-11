import subprocess
import typer

from pathlib import Path
from typing_extensions import Annotated

from ...utils.print_console import print_step, print_success
from ...utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
)

from .env import s3 as s3_env
from .env import google as google_env
from .env import azure as azure_env

app = typer.Typer(no_args_is_help=True)


def copy_template(data):
    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent / "templates" / "django_storages"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context=data
    )


@app.command()
def s3(
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
    Installing django-storages package with S3 backend
    """
    is_project_exists_or_raise()

    print_step("Installing django-storages package with S3 backend ...")
    subprocess.check_call(["uv", "add", "django-storages[s3]"])

    data = {
        "isS3": True,
    }

    copy_template(data)

    s3_env(access_key, secret_key, region_name, bucket_name)

    print_success("django-storages is installed successfully.")


@app.command()
def azure(
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
    Installing django-storages package with Azure backend
    """
    print_step("Installing django-storages package with Azure backend ...")
    subprocess.check_call(["uv", "add", "django-storages[azure]"])

    data = {"isAzure": True}
    copy_template(data)

    azure_env(account_key, account_name, container_name)

    print_success("django-storages is installed successfully.")


@app.command()
def google(
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
    Installing django-storages package with Google backend
    """
    print_step("Installing django-storages package with Google backend ...")
    subprocess.check_call(["uv", "add", "django-storages[google]"])

    data = {"isGoogle": True}
    copy_template(data)

    google_env(credentials_file_path, bucket_name)

    print_success("django-storages is installed successfully.")
