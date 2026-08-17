"""ddx dev database — manage the local pixi-native dev database."""

import shutil
from typing import Optional

import typer

from ..utils.console.print import print_console
from ..utils.django.manage_commands import ManageCommands
from ..utils.project.pixi_runner import PixiRunner
from ..utils.services import BaseDevService, resolve_database_dev_service

app = typer.Typer(no_args_is_help=True)


def _get_service() -> Optional[BaseDevService]:
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
    if not service.is_up():
        service.up()
    service._set_port_env()
    runner = PixiRunner()
    commands = ManageCommands(runner)
    print_console.step("Checking for pending migrations...")
    if commands.migrations_pending():
        print_console.step_done("Migrations pending, applying...")
        commands.run("migrate")
        print_console.ok("Migrations applied")
    else:
        print_console.step_done("No pending migrations")
    print_console.ok(f"{service.display_name} is ready")


@app.command()
def reset() -> None:
    """Flush all data, keeping the service running."""
    service = _get_service()
    service.reset()


@app.command()
def purge() -> None:
    """Stop the service and delete its data under .pixi/devdata/."""
    service = _get_service()
    if service.is_up():
        service.down()
    shutil.rmtree(service.data_dir, ignore_errors=True)
    print_console.ok(f"{service.display_name} data purged")
