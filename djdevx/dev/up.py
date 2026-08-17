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
        if service.is_up():
            print_console.info(f"{service.display_name} is already running")
        else:
            service.up()
            print_console.ok(f"{service.display_name} started")
