"""Package add command."""

from typing import Annotated, Optional

import typer

from ._base import BasePackage
from ._registry import get_package
from .list import list_packages_table
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import add_installable, select_installable
from ..utils.installable.tracking import autocomplete_installable


def _autocomplete_package(incomplete: str) -> list[str]:
    return autocomplete_installable(BasePackage, incomplete)


def add(
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Package name to install", autocompletion=_autocomplete_package
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
    """Install a package."""
    names = (
        select_installable(BasePackage, "package")
        if name is None
        else [name.replace("_", "-")]
    )
    if not names:
        raise typer.Exit()

    is_multi = len(names) > 1
    failed = False

    for pkg_name in names:
        try:
            cls = get_package(pkg_name)
        except KeyError:
            if is_multi:
                print_console.warning(f"Unknown package '{pkg_name}'. Skipping.")
                failed = True
                continue
            print_console.fail(f"Unknown package '{pkg_name}'.")
            list_packages_table()
            raise typer.Exit(code=1)

        try:
            result = add_installable(cls, pkg_name, provider, verbose, is_multi)
            if not result and not is_multi:
                raise typer.Exit()
        except Exception:
            if is_multi:
                print_console.fail(f"Failed to install {pkg_name}. Skipping.")
                failed = True
            else:
                raise

    if is_multi and failed:
        raise typer.Exit(code=1)
