"""Feature add command."""

from typing import Annotated, Optional

import typer

from ._base import BaseFeature
from ._registry import get_feature
from .list import list_features_table
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import add_installable, select_installable
from ..utils.installable.tracking import autocomplete_installable


def _autocomplete_feature(incomplete: str) -> list[str]:
    return autocomplete_installable(BaseFeature, incomplete)


def add(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Feature name to install", autocompletion=_autocomplete_feature
        ),
    ] = None,
    provider: Annotated[
        Optional[str],
        typer.Option("--provider", "-p", help="Variant/provider name"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Install a feature."""
    names = select_installable(BaseFeature, "feature") if name is None else [name]
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

        try:
            result = add_installable(cls, feature_name, provider, verbose, is_multi)
            if not result and not is_multi:
                raise typer.Exit()
        except Exception:
            if is_multi:
                print_console.fail(f"Failed to install {feature_name}. Skipping.")
                failed = True
            else:
                raise

    if is_multi and failed:
        raise typer.Exit(code=1)
