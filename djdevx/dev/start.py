"""ddx dev start — bring up everything then run the dev server."""

from typing import Annotated

import typer

from ..utils.console.print import print_console
from ..utils.django.manage_commands import ManageCommands
from ..utils.project.pixi_runner import PixiRunner
from ..utils.services import resolve_cache_dev_service, resolve_database_dev_service
from .runserver import server_command
from ..settings.source import DEV


def _init_settings() -> None:
    """Reuse the settings commands to init dev configs and secrets (both skip-aware)."""
    from ..settings.configs import init as configs_init
    from ..settings.secrets import init as secrets_init

    configs_init(DEV)
    secrets_init(DEV)


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
    runner = PixiRunner(verbose=verbose)
    commands = ManageCommands(runner)

    if not skip_settings:
        with print_console.step_group(
            "Initializing dev settings...", done="Settings initialized"
        ):
            _init_settings()
    else:
        print_console.step_done("Settings init skipped")

    db_service = resolve_database_dev_service(verbose=verbose)
    if db_service is not None:
        with print_console.step_group(
            "Checking database...", done=f"Found database: {db_service.display_name}"
        ) as group:
            if not db_service.is_up():
                db_service.up(step=group)
            db_service._set_port_env(step=group)
    else:
        print_console.step_done("No database configured")

    if not skip_migrate:
        with print_console.step_group(
            "Checking for pending migrations...", done="Migration check complete"
        ) as group:
            if commands.migrations_pending():
                group.ok("Migrations pending, applying...")
                commands.run("migrate")
                group.info("Migrations applied")
            else:
                group.ok("No pending migrations")
    else:
        print_console.step_done("Migration check skipped")

    cache_service = resolve_cache_dev_service(verbose=verbose)
    if cache_service is not None:
        with print_console.step_group(
            "Checking cache...", done=f"Found cache: {cache_service.display_name}"
        ) as group:
            if not cache_service.is_up():
                cache_service.up(step=group)
            cache_service._set_port_env(step=group)
    else:
        print_console.step_done("No cache configured")

    with print_console.step_group(
        "Starting the dev server ...", done="Dev server started"
    ):
        runner.run_interactive(*server_command(runner), *ctx.args)
