"""Create CLI — create Django apps and components."""

import typer

from .app import startapp as _startapp_cmd

app = typer.Typer(no_args_is_help=True)


@app.command("app")
def create_app(
    name: str = typer.Option(
        "",
        help="Application name",
        prompt="Please enter the application name",
    ),
) -> None:
    """Create a new Django application."""
    _startapp_cmd(name)
