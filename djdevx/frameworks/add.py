"""Framework add command."""

from typing import Annotated, Optional

import typer

from ._base import BaseFramework
from ._registry import get_framework
from .list import list_frameworks_table
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import add_installable, select_installable
from ..utils.installable.tracking import autocomplete_installable


def _autocomplete_framework(incomplete: str) -> list[str]:
    return autocomplete_installable(BaseFramework, incomplete)


def add(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Framework name to add",
            autocompletion=_autocomplete_framework,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Add a CSS/JS framework."""
    names = select_installable(BaseFramework, "framework") if name is None else [name]
    if not names:
        raise typer.Exit()

    for fw_name in names:
        try:
            cls = get_framework(fw_name)
        except KeyError:
            print_console.fail(f"Unknown framework '{fw_name}'.")
            list_frameworks_table()
            raise typer.Exit(code=1)

        add_installable(cls, fw_name, verbose=verbose)
