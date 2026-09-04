"""ddx dev cache — manage the local pixi-native dev cache."""

import typer

from ..utils.console.print import print_console
from ..utils.services import BaseDevService, resolve_cache_dev_service

app = typer.Typer(no_args_is_help=True)


def _get_service() -> BaseDevService | None:
    service = resolve_cache_dev_service()
    if service is None:
        print_console.warning("No cache installed. Run `ddx cache add <name>` first.")
        raise typer.Exit(code=1)
    return service


@app.command()
def init() -> None:
    """Start the dev cache."""
    service = _get_service()
    with print_console.step_group(
        f"Starting {service.display_name}...",
        done=f"{service.display_name} is ready",
    ) as group:
        if not service.is_up():
            service.up(step=group)


@app.command()
def reset() -> None:
    """Flush all data, keeping the service running."""
    service = _get_service()
    with print_console.step_group(
        f"Flushing {service.display_name} data...",
        done=f"{service.display_name} data flushed",
    ) as group:
        service.reset(step=group)


@app.command()
def purge() -> None:
    """Stop the service and delete its data under .pixi/devdata/."""
    service = _get_service()
    service.purge()
