"""Generic data-driven CLI factory for installable domains.

Replaces the five near-identical domain CLI groups (packages, features,
frameworks, database, cache) with one :func:`domain_app` that wires
``add``, ``remove`` and ``list`` commands based on a declarative
configuration, leaving the orchestrator and registry untouched.
"""

from typing import Annotated

import typer

from ..utils.console import prompts
from ..utils.console.print import print_console
from ..utils.installable.discovery import discover_and_register
from ..utils.installable.list_table import build_list_table
from ..utils.installable.orchestrator import add_installable, remove_installable
from ..utils.installable.tracking import (
    autocomplete_installable,
    autocomplete_installed,
    get_display_name,
    get_installable_names,
    get_installed_names,
)


def domain_app(
    base,
    *,
    label: str,
    registry,
    discover_path,
    discover_name: str,
    single: bool = False,
    supports_provider: bool = False,
    supports_multi: bool = False,
) -> typer.Typer:
    """Create a complete Typer sub-app (add / remove / list) for a domain.

    Parameters
    ----------
    base : type
        The domain base class (e.g. ``BasePackage``). Used for registry
        lookup, autocomplete, and the ``list`` command.
    label : str
        Singular display name (e.g. ``"Package"``). Capitalised in help
        text and error messages.
    registry : Registry
        The domain registry instance (e.g. ``PACKAGE_REGISTRY``). Used
        to resolve names in ``get`` / ``list`` calls.
    discover_path : module.__path__
        The ``__path__`` of the domain package (passed to
        :func:`discover_and_register`).
    discover_name : str
        The ``__name__`` of the domain package.
    single : bool
        If True, enforce "only one provider at a time" (database, cache).
    supports_provider : bool
        If True, expose ``--provider / -p`` on add and remove.
    supports_multi : bool
        If True, add/remove support multi-select with ``is_multi`` error
        handling (packages, features).
    """
    discover_and_register(discover_path, discover_name)

    get = registry.get
    label_lower = label.lower()
    label_title = label.capitalize()

    app = typer.Typer(no_args_is_help=True)

    # ------------------------------------------------------------------ list
    @app.command(name="list")
    def list_cmd() -> None:
        """List all available providers in a table."""
        build_list_table(base, label_title)

    # ------------------------------------------------------------------- add
    @app.command(name="add")
    def add_cmd(
        name: Annotated[
            str | None,
            typer.Argument(
                help=f"{label_title} name to install",
                autocompletion=lambda incomplete: autocomplete_installable(
                    base, incomplete
                ),
            ),
        ] = None,
        provider: Annotated[
            str | None,
            typer.Option("--provider", "-p", help="Variant/provider name"),
        ] = None  # noqa: RUF034 — Typer needs this in the signature
        if supports_provider
        else None,
        verbose: Annotated[
            bool,
            typer.Option("--verbose", "-v", help="Show full pixi output"),
        ] = False,
    ) -> None:
        """Install a provider."""
        if single:
            installed = get_installed_names(base)
            if installed:
                existing_name = next(iter(installed))
                print_console.fail(
                    f"A {label_lower} ({existing_name}) is already installed. "
                    f"Only one {label_lower} can be installed at a time."
                )
                raise typer.Exit(code=1)

            if name is None:
                choices = [
                    prompts.Choice(title=get_display_name(base, n), value=n)
                    for n in get_installable_names(base)
                ]
                if not choices:
                    print_console.info(f"All {label_lower}s are already installed.")
                    raise typer.Exit()
                name = prompts.select(
                    f"Which {label_lower} would you like to install?",
                    choices=choices,
                )
                if name is None:
                    raise typer.Exit()
        elif supports_multi:
            names = _select_multi(base, label_lower) if name is None else [name]
            if not names:
                raise typer.Exit()
            _add_multi(names, get, label_lower, list_cmd, provider, verbose)
            return
        elif name is None:
            from ..utils.installable.orchestrator import select_installable

            names = select_installable(base, label_lower)
            if not names:
                raise typer.Exit()
            name = names[0]

        try:
            cls = get(name)
        except KeyError:
            print_console.fail(f"Unknown {label_lower} '{name}'.")
            list_cmd()
            raise typer.Exit(code=1)

        add_installable(cls, name, verbose=verbose)

    # ----------------------------------------------------------------- remove
    @app.command(name="remove")
    def remove_cmd(
        name: Annotated[
            str | None,
            typer.Argument(
                help=f"{label_title} name to remove",
                autocompletion=lambda incomplete: autocomplete_installed(
                    base, incomplete
                ),
            ),
        ] = None,
        provider: Annotated[
            str | None,
            typer.Option("--provider", "-p", help="Variant/provider to remove"),
        ] = None  # noqa: RUF034 — Typer needs this in the signature
        if supports_provider
        else None,
        verbose: Annotated[
            bool,
            typer.Option("--verbose", "-v", help="Show full pixi output"),
        ] = False,
    ) -> None:
        """Remove a provider."""
        if single:
            installed = get_installed_names(base)
            if not installed:
                print_console.warning(f"No {label_lower} installed.")
                return

            if name is None:
                choices = [
                    prompts.Choice(title=get_display_name(base, n), value=n)
                    for n in installed
                ]
                selected = prompts.select(
                    f"Which {label_lower} to remove?", choices=choices
                )
                if selected is None:
                    raise typer.Exit()
                name = selected

            if name not in installed:
                print_console.warning(f"'{name}' is not installed.")
                return

            cls = get(name)
            remove_installable(cls, name, verbose=verbose)
            return
        elif supports_multi:
            names = (
                _select_installed_multi(base, label_lower) if name is None else [name]
            )
            if not names:
                raise typer.Exit()
            _remove_multi(names, get, label_lower, list_cmd, provider, verbose)
            return
        elif name is None:
            from ..utils.installable.orchestrator import select_installed

            names = select_installed(base, label_lower)
            if not names:
                raise typer.Exit()
            name = names[0]

        try:
            cls = get(name)
        except KeyError:
            print_console.fail(f"Unknown {label_lower} '{name}'.")
            list_cmd()
            raise typer.Exit(code=1)

        remove_installable(cls, name, verbose=verbose)

    return app


# ------------------------------------------------------------------
# Multi-select helpers (used by packages / features)
# ------------------------------------------------------------------


def _select_multi(base, label: str) -> list[str] | None:
    """Interactive multi-select from not-yet-installed providers."""
    from ..utils.installable.tracking import get_installable_names

    available = get_installable_names(base)
    if not available:
        print_console.info(f"All {label}s are already installed.")
        return None
    return prompts.checkbox(f"Select {label}s to install:", choices=available)


def _select_installed_multi(base, label: str) -> list[str] | None:
    """Interactive multi-select from already-installed providers."""
    from ..utils.installable.tracking import get_installed_names

    installed = get_installed_names(base)
    if not installed:
        print_console.info(f"No {label}s installed.")
        return None
    return prompts.checkbox(f"Select {label}s to remove:", choices=installed)


def _add_multi(names, get, label, list_cmd, provider, verbose):
    """Add multiple providers with per-item error handling."""
    is_multi = len(names) > 1
    failed = False

    for pkg_name in names:
        try:
            cls = get(pkg_name)
        except KeyError:
            if is_multi:
                print_console.warning(f"Unknown {label} '{pkg_name}'. Skipping.")
                failed = True
                continue
            print_console.fail(f"Unknown {label} '{pkg_name}'.")
            list_cmd()
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


def _remove_multi(names, get, label, list_cmd, provider, verbose):
    """Remove multiple providers with per-item error handling."""
    is_multi = len(names) > 1
    failed = False

    for pkg_name in names:
        try:
            cls = get(pkg_name)
        except KeyError:
            if is_multi:
                print_console.warning(f"Unknown {label} '{pkg_name}'. Skipping.")
                failed = True
                continue
            print_console.fail(f"Unknown {label} '{pkg_name}'.")
            list_cmd()
            raise typer.Exit(code=1)

        result = remove_installable(cls, pkg_name, provider, verbose, is_multi)
        if not result and not is_multi:
            raise typer.Exit()

    if is_multi and failed:
        raise typer.Exit(code=1)
