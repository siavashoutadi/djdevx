"""Create CLI — create Django apps and components."""

import typer
from typing_extensions import Annotated

from ..utils.console import prompts
from .app import startapp as _startapp_cmd

app = typer.Typer(no_args_is_help=True)


@app.command("app")
def create_app(
    name: Annotated[
        str | None,
        typer.Option(help="Application name"),
    ] = None,
) -> None:
    """Create a new Django application."""
    if name is None:
        name = prompts.text("Please enter the application name")
        if name is None:
            raise typer.Abort()
    if not name.strip():
        raise typer.BadParameter("An application name is required.")
    _startapp_cmd(name)
