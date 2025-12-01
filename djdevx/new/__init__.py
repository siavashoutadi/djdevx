import typer

from .backend import app as backend_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(backend_app, name="backend", help="Create a backend only project")
