"""Framework remove command."""

from typing import Annotated, Optional

import typer

from ._base import BaseFramework
from ._registry import get_framework
from .list import list_frameworks_table
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import remove_installable, select_installed
from ..utils.installable.tracking import autocomplete_installed


def _autocomplete_installed_framework(incomplete: str) -> list[str]:
    return autocomplete_installed(BaseFramework, incomplete)


def remove(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Framework name to remove",
            autocompletion=_autocomplete_installed_framework,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Remove a CSS/JS framework."""
    names = select_installed(BaseFramework, "framework") if name is None else [name]
    if not names:
        raise typer.Exit()

    for fw_name in names:
        try:
            cls = get_framework(fw_name)
        except KeyError:
            print_console.fail(f"Unknown framework '{fw_name}'.")
            list_frameworks_table()
            raise typer.Exit(code=1)

        remove_installable(cls, fw_name, verbose=verbose)
