"""ddx dev scheduler — manage the pixi-native Celery Beat daemon."""

import typer

from djdevx.core.console import print_console
from ..utils.devcontainer.detect import in_devcontainer
from ..services import BaseDevService, resolve_scheduler_dev_service

app = typer.Typer(no_args_is_help=True)


def _get_service() -> BaseDevService:
    service = resolve_scheduler_dev_service()
    if service is None:
        print_console.warning(
            "No scheduler is installed. Run `ddx scheduler add celery-beat` first."
        )
        raise typer.Exit(code=1)
    return service


@app.command()
def init() -> None:
    """Start the Celery Beat daemon."""
    if in_devcontainer():
        print_console.info("In a devcontainer: Celery Beat runs via docker compose.")
        return
    service = _get_service()
    with print_console.step_group(
        "Starting Celery Beat...", done="Celery Beat is ready"
    ) as group:
        if not service.is_up():
            service.up(step=group)
    print_console.ok("Celery Beat is ready")


@app.command()
def reset() -> None:
    """Restart Celery Beat (periodic task definitions live in the database)."""
    service = _get_service()
    service.down()
    service.up()
    print_console.ok("Celery Beat restarted")


@app.command()
def purge() -> None:
    """Stop Beat and remove its state under .pixi/devdata/."""
    service = _get_service()
    with print_console.step_group("Purging scheduler", done="purge is done") as group:
        service.purge(step=group)
