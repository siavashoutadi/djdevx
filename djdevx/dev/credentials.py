"""ddx dev credentials — print connection info for installed dev services."""

from djdevx.core.console import print_console
from .context import collect_context
from .render import render_credentials_table


def credentials() -> None:
    """Show how to connect to each installed dev service (host/port/credentials)."""
    context = collect_context()
    if not context.services:
        print_console.info("No dev services configured.")
        return
    render_credentials_table(context)

    if context.in_devcontainer:
        print_console.info(
            "Devcontainer services use fixed hostnames/ports from "
            ".devcontainer/docker-compose.yaml."
        )
