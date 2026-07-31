"""Cache add command."""

from typing import Annotated, Optional

import typer

from ._base import BaseCache
from ._registry import get_cache
from .list import list_caches_table
from ..utils.console import prompts
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import add_installable
from ..utils.installable.tracking import (
    autocomplete_installable,
    get_display_name,
    get_installable_names,
    get_installed_names,
)


def _autocomplete_cache(incomplete: str) -> list[str]:
    return autocomplete_installable(BaseCache, incomplete)


def add(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Cache provider name to install",
            autocompletion=_autocomplete_cache,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Add a cache."""
    installed = get_installed_names(BaseCache)
    if installed:
        existing_name = next(iter(installed))
        print_console.fail(
            f"A cache ({existing_name}) is already installed. "
            "Only one cache can be installed at a time."
        )
        raise typer.Exit(code=1)

    if name is None:
        choices = [
            prompts.Choice(title=get_display_name(BaseCache, n), value=n)
            for n in get_installable_names(BaseCache)
        ]
        if not choices:
            print_console.info("All caches are already installed.")
            raise typer.Exit()
        name = prompts.select("Which cache would you like to install?", choices=choices)
        if name is None:
            raise typer.Exit()

    try:
        cls = get_cache(name)
    except KeyError:
        print_console.fail(f"Unknown cache '{name}'.")
        list_caches_table()
        raise typer.Exit(code=1)

    add_installable(cls, name, verbose=verbose)
