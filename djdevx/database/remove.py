"""Database remove command."""

from typing import Annotated, Optional

import typer

from ._base import BaseDatabase
from ._registry import get_database
from ..utils.console import prompts
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import remove_installable
from ..utils.installable.tracking import (
    autocomplete_installed,
    get_display_name,
    get_installed_names,
)


def _autocomplete_installed_database(incomplete: str) -> list[str]:
    return autocomplete_installed(BaseDatabase, incomplete)


def remove(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Database provider name to remove",
            autocompletion=_autocomplete_installed_database,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Remove a database."""
    installed = get_installed_names(BaseDatabase)
    if not installed:
        print_console.warning("No database installed.")
        return

    if name is None:
        choices = [
            prompts.Choice(title=get_display_name(BaseDatabase, n), value=n)
            for n in installed
        ]
        selected = prompts.select("Which database to remove?", choices=choices)
        if selected is None:
            raise typer.Exit()
        name = selected

    if name not in installed:
        print_console.warning(f"'{name}' is not installed.")
        return

    cls = get_database(name)
    remove_installable(cls, name, verbose=verbose)
