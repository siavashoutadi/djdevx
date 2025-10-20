import typer

from .bootstrap import app as bootstrap_app
from .frankenui import app as frankenui_app
from .semantic import app as semantic_app


app = typer.Typer(no_args_is_help=True)

app.add_typer(
    bootstrap_app,
    name="bootstrap",
    help="Manage bootstrap css framework",
)

app.add_typer(
    frankenui_app,
    name="frankenui",
    help="Manage Franken UI css framework",
)

app.add_typer(
    semantic_app,
    name="semantic",
    help="Manage Semantic css framework",
)
