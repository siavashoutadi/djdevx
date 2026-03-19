import typer

from .packages import list_packages

app = typer.Typer(no_args_is_help=True)

app.command(name="packages", help="List all installed Django packages")(list_packages)
