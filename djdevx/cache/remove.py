"""Cache remove command."""

from typing import Annotated, Optional

import typer

from ._base import BaseCache
from ._registry import get_cache
from ..utils.console import prompts
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import remove_installable
from ..utils.installable.tracking import (
    autocomplete_installed,
    get_display_name,
    get_installed_names,
)


def _autocomplete_installed_cache(incomplete: str) -> list[str]:
    return autocomplete_installed(BaseCache, incomplete)


def remove(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Cache provider name to remove",
            autocompletion=_autocomplete_installed_cache,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Remove a cache."""
    installed = get_installed_names(BaseCache)
    if not installed:
        print_console.warning("No cache installed.")
        return

    if name is None:
        choices = [
            prompts.Choice(title=get_display_name(BaseCache, n), value=n)
            for n in installed
        ]
        selected = prompts.select("Which cache to remove?", choices=choices)
        if selected is None:
            raise typer.Exit()
        name = selected

    if name not in installed:
        print_console.warning(f"'{name}' is not installed.")
        return

    cls = get_cache(name)
    remove_installable(cls, name, verbose=verbose)
