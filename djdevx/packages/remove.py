"""Package remove command."""

from typing import Annotated

import typer

from ._base import BasePackage
from ..utils.installable.types import InstallableConfig
from ._registry import get_package
from .list import list_packages_table
from ..utils.console.print import print_console
from ..utils.installable.orchestrator import remove_installable, select_installed
from ..utils.installable.tracking import autocomplete_installed


def _autocomplete_installed_package(incomplete: str) -> list[str]:
    return autocomplete_installed(BasePackage, incomplete)


def remove(
    name: Annotated[
        str | None,
        typer.Argument(
            help="Package name to remove",
            autocompletion=_autocomplete_installed_package,
        ),
    ] = None,
    provider: Annotated[
        str | None,
        typer.Option("--provider", "-p", help="Variant/provider to remove"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Remove a package or variant."""
    names = (
        select_installed(BasePackage, "package")
        if name is None
        else [InstallableConfig.normalize_name(name)]
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

        result = remove_installable(cls, pkg_name, provider, verbose, is_multi)
        if not result and not is_multi:
            raise typer.Exit()

    if is_multi and failed:
        raise typer.Exit(code=1)
