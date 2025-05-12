import typer

from .app import startapp

app = typer.Typer(no_args_is_help=True)

app.command(name="app", help="Create a new Django application")(startapp)
