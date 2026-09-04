"""ddx dev start — bring up everything then run the dev server."""

from typing import Annotated

import typer

from ..cli.dev import run_start


def start(
    ctx: typer.Context,
    skip_settings: Annotated[
        bool,
        typer.Option("--skip-settings", help="Skip settings configs/secrets init"),
    ] = False,
    skip_migrate: Annotated[
        bool,
        typer.Option("--skip-migrate", help="Skip database migrations"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full pixi output"),
    ] = False,
) -> None:
    """Start the local dev environment (idempotent) and run the dev server.

    Any additional arguments are forwarded to the dev server command.
    """
    run_start(
        ctx, skip_settings=skip_settings, skip_migrate=skip_migrate, verbose=verbose
    )
