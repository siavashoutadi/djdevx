"""ddx dev — local development environment command group.

Postgres/Redis run natively via pixi; the Celery worker/Beat run as pixi
daemons, and OTel runs native binaries. Data lives under ``.pixi/devdata/``.
No Docker required.
"""

import typer

from .cache import app as cache_app
from .credentials import credentials as _credentials
from .database import app as database_app
from .down import down as _down
from .otel import app as otel_app
from .runserver import runserver as _runserver
from .scheduler import app as scheduler_app
from .start import start as _start
from .status import status as _status
from .task_queue import app as task_queue_app
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
app.add_typer(otel_app, name="otel", help="Manage the local dev OTel stack")
app.add_typer(task_queue_app, name="task-queue", help="Manage the local dev task queue")
app.add_typer(scheduler_app, name="scheduler", help="Manage the local dev scheduler")
