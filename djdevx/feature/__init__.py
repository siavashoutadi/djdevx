import typer

from .startapp import app as startapp


app = typer.Typer(no_args_is_help=True)

app.add_typer(startapp)
