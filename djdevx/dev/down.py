"""ddx dev down — stop installed dev services (db, cache, otel, worker, beat)."""

from djdevx.core.console import print_console
from ..services import resolve_dev_services


def down() -> None:
    """Stop installed database/cache/otel/task-queue/scheduler services."""
    services = resolve_dev_services()
    if not services:
        print_console.info("No dev services installed.")
        return
    for service in services:
        with print_console.step_group(
            f"Stopping {service.display_name}...",
            done=f"{service.display_name} stopped",
        ) as group:
            if service.is_up():
                service.down(step=group)
