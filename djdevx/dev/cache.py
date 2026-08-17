"""ddx dev cache — manage the local pixi-native dev cache."""

import shutil
from typing import Optional

import typer

from ..utils.console.print import print_console
from ..utils.services import BaseDevService, resolve_cache_dev_service

app = typer.Typer(no_args_is_help=True)


def _get_service() -> Optional[BaseDevService]:
    service = resolve_cache_dev_service()
    if service is None:
        print_console.warning("No cache installed. Run `ddx cache add <name>` first.")
        raise typer.Exit(code=1)
    return service


@app.command()
def init() -> None:
    """Start the dev cache."""
    service = _get_service()
    if not service.is_up():
        service.up()
    print_console.ok(f"{service.display_name} is ready")


@app.command()
def reset() -> None:
    """Flush all data, keeping the service running."""
    service = _get_service()
    service.reset()
    print_console.ok(f"{service.display_name} data flushed")


@app.command()
def purge() -> None:
    """Stop the service and delete its data under .pixi/devdata/."""
    service = _get_service()
    if service.is_up():
        service.down()
    shutil.rmtree(service.data_dir, ignore_errors=True)
    print_console.ok(f"{service.display_name} data purged")
