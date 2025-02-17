import subprocess
import typer

from typing import Annotated
from pathlib import Path

from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
)


app = typer.Typer(no_args_is_help=True)


@app.command()
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
    is_project_exists_or_raise()

    subprocess.run(["uv", "run", "manage.py", "startapp", application_name])

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent.parent / "templates" / "startapp"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir,
        dest_dir=project_dir,
        template_context={"application_name": application_name},
    )
