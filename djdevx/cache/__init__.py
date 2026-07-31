"""Cache CLI — add/remove/list caches with auto-discovery."""

import typer

from ..utils.installable.discovery import discover_and_register
from .add import add as _add
from .remove import remove as _remove
from .list import list_caches_table as _list

app = typer.Typer(no_args_is_help=True)

discover_and_register(__path__, __name__)

app.command(name="add")(_add)
app.command(name="remove")(_remove)
app.command(name="list")(_list)
