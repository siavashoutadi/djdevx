"""ddx dev task-queue — manage the pixi-native Celery worker daemon."""

import typer

from djdevx.core.console import print_console
from ..utils.devcontainer.detect import in_devcontainer
from ..services import BaseDevService, resolve_task_queue_dev_service

app = typer.Typer(no_args_is_help=True)


def _get_service() -> BaseDevService:
    service = resolve_task_queue_dev_service()
    if service is None:
        print_console.warning(
            "No task queue is installed. Run `ddx task-queue add celery` first."
        )
        raise typer.Exit(code=1)
    return service


@app.command()
def init() -> None:
    """Start the Celery worker daemon."""
    if in_devcontainer():
        print_console.info(
            "In a devcontainer: the Celery worker runs via docker compose."
        )
        return
    service = _get_service()
    with print_console.step_group(
        "Starting Celery worker...", done="Celery worker is ready"
    ) as group:
        if not service.is_up():
            service.up(step=group)
    print_console.ok("Celery worker is ready")


@app.command()
def reset() -> None:
    """Restart the Celery worker (tasks have no queue-backed data to flush)."""
    service = _get_service()
    service.down()
    service.up()
    print_console.ok("Celery worker restarted")


@app.command()
def purge() -> None:
    """Stop the worker and remove its state under .pixi/devdata/."""
    service = _get_service()
    with print_console.step_group("Purging task queue", done="purge is done") as group:
        service.purge(step=group)
