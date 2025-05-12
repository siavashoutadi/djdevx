import typer

from .pwa import app as pwa


app = typer.Typer(no_args_is_help=True)

app.add_typer(pwa)
