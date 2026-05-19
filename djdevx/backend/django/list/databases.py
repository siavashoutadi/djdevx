"""List installed Django databases tracked by djdevx."""

import typer
import tomlkit

from ....utils.console.print import print_console
from ....utils.djdevx_config.backend.database_tracker import DatabaseTracker


def list_databases() -> None:
    """List all installed Django databases from .djdevx/backend/django/database/."""
    tracker = DatabaseTracker()
    database_root = tracker._database_root

    if not database_root.exists():
        print_console.warning(
            "No databases installed yet. The .djdevx/backend/django/database/ directory does not exist."
        )
        raise typer.Exit(0)

    config_files = sorted(database_root.rglob("config.toml"))

    if not config_files:
        print_console.warning("No databases installed yet.")
        raise typer.Exit(0)

    print_console.step("Installed databases:")
    for config_file in config_files:
        try:
            doc = tomlkit.parse(config_file.read_text())
            name = doc.get("database", {}).get("name", "unknown")
        except Exception:
            name = "unknown"
        print_console.info(f"  - {name}")
