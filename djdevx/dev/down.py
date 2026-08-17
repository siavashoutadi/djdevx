"""ddx dev down — stop installed database/cache services."""

from ..utils.console.print import print_console
from ..utils.services import resolve_dev_services


def down() -> None:
    """Stop installed database/cache services."""
    services = resolve_dev_services()
    if not services:
        print_console.info("No database or cache installed.")
        return
    for service in services:
        if service.is_up():
            service.down()
            print_console.ok(f"{service.display_name} stopped")
