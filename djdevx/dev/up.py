"""ddx dev up — start installed dev services (db, cache, otel, worker, beat)."""

from djdevx.core.console import print_console
from ..services import resolve_dev_services


def up() -> None:
    """Start installed database/cache/otel/task-queue/scheduler services (pixi-native, idempotent)."""
    services = resolve_dev_services()
    if not services:
        print_console.info("No dev services installed.")
        return
    for service in services:
        with print_console.step_group(
            f"Starting {service.display_name}...",
            done=f"{service.display_name} started",
        ) as group:
            if service.is_up():
                group.info(f"{service.display_name} is already running")
                service._set_port_env(step=group)
            else:
                service.up(step=group)
