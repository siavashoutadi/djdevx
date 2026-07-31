"""Database add command."""

from typing import Annotated, Optional

import typer

from ._base import BaseDatabase
from ._registry import get_database
from .list import list_databases_table
from ..utils.console import prompts
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import add_installable
from ..utils.installable.tracking import (
    autocomplete_installable,
    get_display_name,
    get_installable_names,
    get_installed_names,
)


def _autocomplete_database(incomplete: str) -> list[str]:
    return autocomplete_installable(BaseDatabase, incomplete)


def add(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Database provider name to install",
            autocompletion=_autocomplete_database,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Add a database."""
    installed = get_installed_names(BaseDatabase)
    if installed:
        existing_name = next(iter(installed))
        print_console.fail(
            f"A database ({existing_name}) is already installed. "
            "Only one database can be installed at a time."
        )
        raise typer.Exit(code=1)

    if name is None:
        choices = [
            prompts.Choice(title=get_display_name(BaseDatabase, n), value=n)
            for n in get_installable_names(BaseDatabase)
        ]
        if not choices:
            print_console.info("All databases are already installed.")
            raise typer.Exit()
        name = prompts.select(
            "Which database would you like to install?", choices=choices
        )
        if name is None:
            raise typer.Exit()

    try:
        cls = get_database(name)
    except KeyError:
        print_console.fail(f"Unknown database '{name}'.")
        list_databases_table()
        raise typer.Exit(code=1)

    add_installable(cls, name, verbose=verbose)
