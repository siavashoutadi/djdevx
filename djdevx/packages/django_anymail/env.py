import typer

from typing_extensions import Annotated

from ...utils.print_console import print_step, print_success
from ...utils.project_files import (
    is_project_exists_or_raise,
    add_env_varibles,
)


app = typer.Typer(no_args_is_help=True)


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
    Creating environment variables for django-anymail with SES backend
    """
    is_project_exists_or_raise()

    print_step("Creating environment variables for django-anymail with SES backend ...")

    add_env_varibles(key="ANYMAIL_SES_ACCESS_KEY", value=access_key)
    add_env_varibles(key="ANYMAIL_SES_SECRET_KEY", value=secret_key)
    add_env_varibles(key="ANYMAIL_SES_REGION_NAME", value=region_name)

    print_success("django-anymail environment variables are configured successfully.")


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
    Creating environment variables for django-anymail with brevo backend
    """
    is_project_exists_or_raise()

    print_step(
        "Creating environment variables for django-anymail with brevo backend ..."
    )

    add_env_varibles(key="ANYMAIL_BREVO_API_KEY", value=api_key)

    print_success("django-anymail environment variables are configured successfully.")


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
):
    """
    Creating environment variables for django-anymail with mailgun backend
    """
    is_project_exists_or_raise()

    print_step(
        "Creating environment variables for django-anymail with mailgun backend ..."
    )

    add_env_varibles(key="ANYMAIL_MAILGUN_API_KEY", value=api_key)

    print_success("django-anymail environment variables are configured successfully.")


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
    Creating environment variables for django-anymail with mailjet backend
    """
    is_project_exists_or_raise()

    print_step(
        "Creating environment variables for django-anymail with mailjet backend ..."
    )

    add_env_varibles(key="ANYMAIL_MAILJET_API_KEY", value=api_key)
    add_env_varibles(key="ANYMAIL_MAILJET_SECRET_KEY", value=secret_key)

    print_success("django-anymail environment variables are configured successfully.")


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
    Creating environment variables for django-anymail with resend backend
    """
    is_project_exists_or_raise()

    print_step(
        "Creating environment variables for django-anymail with resend backend ..."
    )

    add_env_varibles(key="ANYMAIL_RESEND_API_KEY", value=api_key)

    print_success("django-anymail environment variables are configured successfully.")
