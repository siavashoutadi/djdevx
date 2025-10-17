import typer

from .bootstrap import app as bootstrap_app


app = typer.Typer(no_args_is_help=True)

app.add_typer(
    bootstrap_app,
    name="bootstrap",
    help="Manage bootstrap css framework",
)
