"""Declarative ``ddx dev start`` pipeline.

Replaces the manual if/else chain that used to live in ``dev/start.py`` with an
ordered, named list of steps. The steps mirror the previous behaviour exactly:

    1. settings init   — dev configs + secrets (skip with ``--skip-settings``)
    2. database        — start the installed database service (if any)
    3. migrate         — apply pending migrations (skip with ``--skip-migrate``)
    4. cache           — start the installed cache service (if any)
    5. render          — print the resolved service endpoints table
    6. server          — run the dev server (forwards extra args)

Steps 2-4 are folded into :func:`_services_step`, which also handles the
devcontainer case (services are managed by docker compose, so only migrate runs).

The redundant double-start loop that previously restarted postgres/redis a
second time is removed: each native service is started exactly once.
"""

import typer

from ..settings.source import DEV
from djdevx.core.console import print_console
from ..utils.devcontainer.detect import in_devcontainer
from ..utils.django.manage_commands import ManageCommands
from djdevx.core.process import PixiRunner
from ..services import (
    BaseDevService,
    resolve_cache_dev_service,
    resolve_database_dev_service,
)
from .context import collect_context
from .render import render_services_table
from .runserver import server_command


def _init_settings() -> None:
    """Reuse the settings commands to init dev configs and secrets (both skip-aware)."""
    from ..settings.configs import init as configs_init
    from ..settings.secrets import init as secrets_init

    configs_init(DEV)
    secrets_init(DEV)


def _settings_step(skip_settings: bool) -> None:
    if skip_settings:
        print_console.step_done("Settings init skipped")
        return
    with print_console.step_group(
        "Initializing dev settings...", done="Settings initialized"
    ):
        _init_settings()


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


def _services_step(commands: ManageCommands, skip_migrate: bool, verbose: bool) -> None:
    """Start db, migrate, then start cache (or only migrate in a devcontainer)."""
    if in_devcontainer():
        print_console.step_done(
            "Running inside a devcontainer — services are managed by docker compose"
        )
        _migrate_if_pending(commands, skip_migrate)
        return

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


def _server_step(ctx: typer.Context, runner: PixiRunner, verbose: bool) -> None:
    with print_console.step_group(
        "Starting the dev server ...", done="Dev server started"
    ):
        runner.run_interactive(*server_command(runner), *ctx.args)


def run_start(
    ctx: typer.Context,
    *,
    skip_settings: bool = False,
    skip_migrate: bool = False,
    verbose: bool = False,
) -> None:
    """Run the declarative ``dev start`` pipeline, then start the dev server.

    Inside a devcontainer the database/redis services are started by the
    devcontainer compose, so only settings/migrations/server run here. On a
    plain machine the pixi-native services are started. In both cases the
    resolved service endpoints are printed before the server starts.
    """
    runner = PixiRunner(verbose=verbose)
    commands = ManageCommands(runner)

    _settings_step(skip_settings)
    _services_step(commands, skip_migrate, verbose)
    render_services_table(collect_context(verbose=verbose))
    _server_step(ctx, runner, verbose)
