"""Feature remove command."""

from typing import Annotated, Optional

import typer

from ._base import BaseFeature
from ._registry import get_feature
from .list import list_features_table
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import remove_installable, select_installed
from ..utils.installable.tracking import autocomplete_installed


def _autocomplete_installed_feature(incomplete: str) -> list[str]:
    return autocomplete_installed(BaseFeature, incomplete)


def remove(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Feature name to remove",
            autocompletion=_autocomplete_installed_feature,
        ),
    ] = None,
    provider: Annotated[
        Optional[str],
        typer.Option("--provider", "-p", help="Variant/provider to remove"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Remove a feature or variant."""
    names = select_installed(BaseFeature, "feature") if name is None else [name]
    if not names:
        raise typer.Exit()

    is_multi = len(names) > 1
    failed = False

    for feature_name in names:
        try:
            cls = get_feature(feature_name)
        except KeyError:
            if is_multi:
                print_console.warning(f"Unknown feature '{feature_name}'. Skipping.")
                failed = True
                continue
            print_console.fail(f"Unknown feature '{feature_name}'.")
            list_features_table()
            raise typer.Exit(code=1)

        result = remove_installable(cls, feature_name, provider, verbose, is_multi)
        if not result and not is_multi:
            raise typer.Exit()

    if is_multi and failed:
        raise typer.Exit(code=1)
