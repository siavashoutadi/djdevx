"""ddx dev otel — manage the local pixi-native otel collector + openobserve."""

import typer

from ..utils.console.print import print_console
from ..utils.devcontainer.detect import in_devcontainer
from ..utils.services import BaseDevService, resolve_otel_dev_services

app = typer.Typer(no_args_is_help=True)


def _get_services() -> list[BaseDevService]:
    services = resolve_otel_dev_services()
    if not services:
        print_console.warning(
            "OpenTelemetry is not installed. Run `ddx features add otel` first."
        )
        raise typer.Exit(code=1)
    return services


@app.command()
def init() -> None:
    """Start the otel collector and OpenObserve."""
    if in_devcontainer():
        print_console.info(
            "In a devcontainer: otel services are started by docker compose."
        )
        return
    for service in _get_services():
        service.up()
    print_console.ok("OTel services are ready")


@app.command()
def reset() -> None:
    """Flush telemetry data, keeping the services running."""
    for service in _get_services():
        service.reset()
    print_console.ok("OTel data flushed")


@app.command()
def purge() -> None:
    """Stop the services and delete their data under .pixi/devdata/."""
    services = _get_services()
    group = print_console.step_group("Purging OTel", done="purge is done")
    try:
        for service in services:
            service.purge(step=group)
    finally:
        group.done()
