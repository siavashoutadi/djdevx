import typer

from .postgres import app as postgres_app

app = typer.Typer(no_args_is_help=True)
app.add_typer(postgres_app, name="postgres", help="PostgreSQL database management")
