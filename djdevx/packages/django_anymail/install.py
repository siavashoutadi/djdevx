import subprocess
import typer

from pathlib import Path
from typing_extensions import Annotated

from ...utils.print_console import print_step, print_success
from ...utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
    add_env_varibles,
)


app = typer.Typer(no_args_is_help=True)


def copy_template(data):
    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent.parent / "templates" / "django_anymail"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context=data
    )


@app.command()
def ses(
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
    Installing django-anymail with SES backend
    """
    is_project_exists_or_raise()

    print_step("Installing django-anymail with SES backend ...")
    subprocess.check_call(["uv", "add", "django-anymail[amazon-ses]"])

    data = {
        "isSES": True,
    }

    copy_template(data)

    add_env_varibles(key="ANYMAIL_SES_ACCESS_KEY", value=access_key)
    add_env_varibles(key="ANYMAIL_SES_SECRET_KEY", value=secret_key)
    add_env_varibles(key="ANYMAIL_SES_REGION_NAME", value=region_name)

    print_success("django-anymail is installed successfully.")


@app.command()
def brevo(
    api_key: Annotated[
        str,
        typer.Option(
            help="The Brevo API key for authentication",
            prompt="Please enter the Brevo API key for authentication",
            hide_input=True,
        ),
    ],
):
    """
    Installing django-anymail with brevo backend
    """
    is_project_exists_or_raise()

    print_step("Installing django-anymail with brevo backend ...")
    subprocess.check_call(["uv", "add", "django-anymail"])

    data = {
        "isBrevo": True,
    }

    copy_template(data)

    add_env_varibles(key="ANYMAIL_BREVO_API_KEY", value=api_key)

    print_success("django-anymail is installed successfully.")


@app.command()
def mailgun(
    api_key: Annotated[
        str,
        typer.Option(
            help="The Mailgun API key for authentication",
            prompt="Please enter the Mailgun API key for authentication",
            hide_input=True,
        ),
    ],
    is_europe_region: Annotated[
        bool,
        typer.Option(
            help="If you are using the Europe region",
            prompt="Are you using the Europe region",
        ),
    ],
):
    """
    Installing django-anymail with mailgun backend
    """
    is_project_exists_or_raise()

    print_step("Installing django-anymail with mailgun backend ...")
    subprocess.check_call(["uv", "add", "django-anymail"])

    data = {
        "isMailgun": True,
        "mailgun_api_url": "https://api.mailgun.net/v3"
        if is_europe_region
        else "https://api.eu.mailgun.net/v3",
    }

    copy_template(data)

    add_env_varibles(key="ANYMAIL_MAILGUN_API_KEY", value=api_key)

    print_success("django-anymail is installed successfully.")


@app.command()
def mailjet(
    api_key: Annotated[
        str,
        typer.Option(
            help="The Mailjet API key for authentication",
            prompt="Please enter the Mailjet API key for authentication",
        ),
    ],
    secret_key: Annotated[
        str,
        typer.Option(
            help="The Mailjet secret key for authentication",
            prompt="Please enter the Mailjet secret key for authentication",
            hide_input=True,
        ),
    ],
):
    """
    Installing django-anymail with mailjet backend
    """
    is_project_exists_or_raise()

    print_step("Installing django-anymail with mailjet backend ...")
    subprocess.check_call(["uv", "add", "django-anymail"])

    data = {
        "isMailjet": True,
    }

    copy_template(data)

    add_env_varibles(key="ANYMAIL_MAILJET_API_KEY", value=api_key)
    add_env_varibles(key="ANYMAIL_MAILJET_SECRET_KEY", value=secret_key)

    print_success("django-anymail is installed successfully.")


@app.command()
def resend(
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
    Installing django-anymail with resend backend
    """
    is_project_exists_or_raise()

    print_step("Installing django-anymail with resend backend ...")
    subprocess.check_call(["uv", "add", "django-anymail[resend]"])

    data = {
        "isResend": True,
    }

    copy_template(data)

    add_env_varibles(key="ANYMAIL_RESEND_API_KEY", value=api_key)

    print_success("django-anymail is installed successfully.")
