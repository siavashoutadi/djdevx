"""List installed Django packages tracked by djdevx."""

import tomllib

import typer

from ....utils.console.print import print_console
from ....utils.djdevx_config.project import ProjectConfig


def list_packages() -> None:
    """List all installed Django packages from .djdevx/backend/django/packages/."""
    config = ProjectConfig()
    packages_root = config.djdevx_root / "backend" / "django" / "packages"

    if not packages_root.exists():
        print_console.warning(
            "No packages installed yet. The .djdevx/backend/django/packages/ directory does not exist."
        )
        raise typer.Exit(0)

    config_files = sorted(packages_root.rglob("config.toml"))

    if not config_files:
        print_console.warning("No packages installed yet.")
        raise typer.Exit(0)

    print_console.step("Installed packages:")
    for config_file in config_files:
        with open(config_file, "rb") as f:
            data = tomllib.load(f)
        name = data.get("package", {}).get("name", "unknown")
        print_console.info(f"  - {name}")
