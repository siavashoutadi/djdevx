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

app = typer.Typer(no_args_is_help=True)


def copy_template(data):
    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent.parent / "templates" / "django_allauth"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir, dest_dir=project_dir, template_context=data
    )


@app.command()
def account(
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
    Installing django-allauth package
    """
    is_project_exists_or_raise()

    print_step("Installing django-allauth package ...")
    subprocess.check_call(["uv", "add", "django-allauth"])
    if is_profanity_for_username_enabled:
        subprocess.check_call(["uv", "add", "better-profanity"])

    data = {
        "email_subject_prefix": email_subject_prefix,
        "is_profanity_for_username_enabled": is_profanity_for_username_enabled,
        "account_url_prefix": account_url_prefix,
    }

    copy_template(data)

    print_success("django-allauth is installed successfully.")
