import typer

from .pwa import app as pwa
from .css import app as css


app = typer.Typer(no_args_is_help=True)

app.add_typer(pwa)
app.add_typer(css, name="css", help="Manage css frameworks")
