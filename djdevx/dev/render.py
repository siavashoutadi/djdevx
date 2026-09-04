"""Shared rendering for dev service tables (start, status, credentials)."""

from djdevx.core.console import print_console
from ..utils.devcontainer.detect import DevelopmentContext


def render_services_table(context: DevelopmentContext) -> None:
    """Print the running/exposed services as a Rich table."""
    if not context.services:
        print_console.info("No dev services configured.")
        return
    title = (
        "Dev services (devcontainer / docker compose)"
        if context.in_devcontainer
        else "Dev services (pixi-native)"
    )
    with print_console.table(
        title,
        [
            ("Service", {"style": "bold", "min_width": 14, "no_wrap": True}),
            ("Host", {"no_wrap": True}),
            ("Port", {"justify": "right", "no_wrap": True}),
            ("URL", {"min_width": 24}),
        ],
    ) as tbl:
        for svc in context.services:
            port = str(svc.port) if svc.port else "-"
            tbl.add_row(svc.display_name, svc.host, port, svc.url or "")


def render_credentials_table(context: DevelopmentContext) -> None:
    """Print per-service connect blocks (host/port/credentials/URL, no tables)."""
    if not context.services:
        print_console.info("No dev services configured.")
        return
    if context.in_devcontainer:
        print_console.info("Credentials (devcontainer / docker compose)")
    else:
        print_console.info("Credentials (pixi-native)")
    for svc in context.services:
        print_console.section(svc.display_name)
        print_console.info(f"  Host: {svc.host}")
        if svc.port:
            print_console.info(f"  Port: {svc.port}")
        if svc.credentials:
            print_console.info(f"  Credentials: {svc.credentials}")
        if svc.url:
            print_console.link(f"  URL: {svc.url}", svc.url)
        print_console.rule()
