"""ddx dev — local development environment command group.

Postgres/Redis run natively via pixi conda packages; data lives under
``.pixi/devdata/``. No Docker required.
"""

import typer

from .cache import app as cache_app
from .credentials import credentials as _credentials
from .database import app as database_app
from .down import down as _down
from .runserver import runserver as _runserver
from .start import start as _start
from .status import status as _status
from .up import up as _up

app = typer.Typer(no_args_is_help=True)

app.command(
    name="start",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)(_start)
app.command(
    name="runserver",
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
        "help_option_names": [],
    },
)(_runserver)
app.command(name="up")(_up)
app.command(name="down")(_down)
app.command(name="status")(_status)
app.command(name="credentials")(_credentials)
app.add_typer(database_app, name="database", help="Manage the local dev database")
app.add_typer(cache_app, name="cache", help="Manage the local dev cache")
