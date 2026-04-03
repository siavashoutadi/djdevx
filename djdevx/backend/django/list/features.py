"""List installed Django features tracked by djdevx."""

import typer
import tomlkit

from ....utils.console.print import print_console
from ....utils.djdevx_config.backend.feature_tracker import FeatureTracker


def list_features() -> None:
    """List all installed Django features from .djdevx/backend/django/features/."""
    tracker = FeatureTracker()
    features_root = tracker._features_root

    if not features_root.exists():
        print_console.warning(
            "No features installed yet. The .djdevx/backend/django/features/ directory does not exist."
        )
        raise typer.Exit(0)

    config_files = sorted(features_root.rglob("config.toml"))

    if not config_files:
        print_console.warning("No features installed yet.")
        raise typer.Exit(0)

    print_console.step("Installed features:")
    for config_file in config_files:
        try:
            doc = tomlkit.parse(config_file.read_text())
            name = doc.get("feature", {}).get("name", "unknown")
        except Exception:
            name = "unknown"
        print_console.info(f"  - {name}")
