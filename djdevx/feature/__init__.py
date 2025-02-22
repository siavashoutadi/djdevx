import typer

from .startapp import app as startapp
from .pwa import app as pwa


app = typer.Typer(no_args_is_help=True)

app.add_typer(startapp)
app.add_typer(pwa)
