"""ddx dev database — manage the local pixi-native dev database."""

import typer

from djdevx.core.console import print_console
from ..utils.django.manage_commands import ManageCommands
from djdevx.core.process import PixiRunner
from ..services import BaseDevService, resolve_database_dev_service

app = typer.Typer(no_args_is_help=True)


def _get_service() -> BaseDevService | None:
    service = resolve_database_dev_service()
    if service is None:
        print_console.warning(
            "No database installed. Run `ddx database add <name>` first."
        )
        raise typer.Exit(code=1)
    return service


@app.command()
def init() -> None:
    """Start the dev database and apply pending migrations."""
    service = _get_service()
    with print_console.step_group(
        f"Starting {service.display_name}...",
        done=f"{service.display_name} is ready",
    ) as group:
        if not service.is_up():
            service.up(step=group)
        service._set_port_env(quiet=False, step=group)
    runner = PixiRunner()
    commands = ManageCommands(runner)
    with print_console.step_group(
        "Checking for pending migrations...", done="Migration check complete"
    ) as group:
        if commands.migrations_pending():
            group.ok("Migrations pending, applying...")
            commands.run("migrate")
            group.info("Migrations applied")
        else:
            group.ok("No pending migrations")


@app.command()
def reset() -> None:
    """Flush all data, keeping the service running."""
    service = _get_service()
    service.reset()


@app.command()
def purge() -> None:
    """Stop the service and delete its data under .pixi/devdata/."""
    service = _get_service()
    service.purge()
