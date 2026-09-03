"""ddx dev start — bring up everything then run the dev server."""

from typing import Annotated

import typer

from ..utils.console.print import print_console
from ..utils.devcontainer.detect import in_devcontainer
from ..utils.django.manage_commands import ManageCommands
from ..utils.project.pixi_runner import PixiRunner
from ..utils.services import (
    BaseDevService,
    resolve_cache_dev_service,
    resolve_database_dev_service,
    resolve_dev_services,
)
from .context import collect_context
from .render import render_services_table
from .runserver import server_command
from ..settings.source import DEV


def _init_settings() -> None:
    """Reuse the settings commands to init dev configs and secrets (both skip-aware)."""
    from ..settings.configs import init as configs_init
    from ..settings.secrets import init as secrets_init

    configs_init(DEV)
    secrets_init(DEV)


def _start_native_service(service: BaseDevService) -> None:
    """Start a single pixi-native dev service (idempotent)."""
    with print_console.step_group(
        f"Checking {service.display_name}...",
        done=f"Found {service.display_name}",
    ) as group:
        if not service.is_up():
            service.up(step=group)
        service._set_port_env(step=group)


def _migrate_if_pending(commands: ManageCommands, skip_migrate: bool) -> None:
    if skip_migrate:
        print_console.step_done("Migration check skipped")
        return
    with print_console.step_group(
        "Checking for pending migrations...", done="Migration check complete"
    ) as group:
        if commands.migrations_pending():
            group.ok("Migrations pending, applying...")
            commands.run("migrate")
            group.info("Migrations applied")
        else:
            group.ok("No pending migrations")


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

    Inside a devcontainer the database/redis services are started by the
    devcontainer compose, so only settings/migrations/server run here. On a
    plain machine the pixi-native services are started. In both cases the
    resolved service endpoints are printed.

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

    if in_devcontainer():
        print_console.step_done(
            "Running inside a devcontainer — services are managed by docker compose"
        )
        _migrate_if_pending(commands, skip_migrate)
    else:
        db_service = resolve_database_dev_service(verbose=verbose)
        if db_service is not None:
            _start_native_service(db_service)
        else:
            print_console.step_done("No database configured")

        _migrate_if_pending(commands, skip_migrate)

        cache_service = resolve_cache_dev_service(verbose=verbose)
        if cache_service is not None:
            _start_native_service(cache_service)
        else:
            print_console.step_done("No cache configured")

        for service in resolve_dev_services(verbose=verbose):
            if service.name in ("postgres", "redis"):
                _start_native_service(service)

    render_services_table(collect_context(verbose=verbose))

    with print_console.step_group(
        "Starting the dev server ...", done="Dev server started"
    ):
        runner.run_interactive(*server_command(runner), *ctx.args)
