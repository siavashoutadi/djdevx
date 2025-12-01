import typer

from typing import Annotated
from pathlib import Path

from ....utils.django.uv_runner import UvRunner
from ....utils.django.project_manager import DjangoProjectManager


app = typer.Typer(no_args_is_help=True)


def startapp(
    application_name: Annotated[
        str,
        typer.Option(
            help="Application name",
            prompt="Please enter the application name",
        ),
    ] = "",
):
    """
    Create a new Django application
    """
    pm = DjangoProjectManager()

    uv_runner = UvRunner()
    uv_runner.run_manage_command("startapp", application_name)

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent.parent / "templates" / "django" / "startapp"

    pm.copy_templates(
        source_dir=source_dir,
        template_context={"application_name": application_name},
    )
