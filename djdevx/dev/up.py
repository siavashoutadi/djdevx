"""ddx dev up — start installed database/cache services."""

from ..utils.console.print import print_console
from ..utils.services import resolve_dev_services


def up() -> None:
    """Start installed database/cache services (pixi-native, idempotent)."""
    services = resolve_dev_services()
    if not services:
        print_console.info("No database or cache installed.")
        return
    for service in services:
        with print_console.step_group(
            f"Starting {service.display_name}...",
            done=f"{service.display_name} started",
        ) as group:
            if service.is_up():
                group.info(f"{service.display_name} is already running")
            else:
                service.up(step=group)
