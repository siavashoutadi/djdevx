"""List installed Django caches tracked by djdevx."""

import typer
import tomlkit

from ....utils.console.print import print_console
from ....utils.djdevx_config.backend.cache_tracker import CacheTracker


def list_caches() -> None:
    """List all installed Django caches from .djdevx/backend/django/cache/."""
    tracker = CacheTracker()
    cache_root = tracker._cache_root

    if not cache_root.exists():
        print_console.warning(
            "No caches installed yet. The .djdevx/backend/django/cache/ directory does not exist."
        )
        raise typer.Exit(0)

    config_files = sorted(cache_root.rglob("config.toml"))

    if not config_files:
        print_console.warning("No caches installed yet.")
        raise typer.Exit(0)

    print_console.step("Installed caches:")
    for config_file in config_files:
        try:
            doc = tomlkit.parse(config_file.read_text())
            name = doc.get("cache", {}).get("name", "unknown")
        except Exception:
            name = "unknown"
        print_console.info(f"  - {name}")
