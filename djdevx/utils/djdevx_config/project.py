import typer
import tomllib
from pathlib import Path

from ..console.print import print_console


class ProjectConfig:
    """
    Reads and exposes data from the root .djdevx/config.toml.
    Scope: everything under .djdevx/ that is not backend/frontend specific.
    """

    def __init__(self):
        self._config_data = None

    @property
    def project_root_dir(self) -> Path:
        """Directory that contains the .djdevx/ folder."""
        current = Path.cwd()
        if (current / ".djdevx" / "config.toml").exists():
            return current
        print_console.error(
            "Is this a project managed by djdevx? Are you running from the root of your project?"
        )
        raise typer.Exit(1)

    @property
    def djdevx_root(self) -> Path:
        """The .djdevx/ directory itself."""
        return self.project_root_dir / ".djdevx"

    @property
    def config_path(self) -> Path:
        """Path to .djdevx/config.toml."""
        path = self.djdevx_root / "config.toml"
        if not path.exists():
            print_console.error(
                "Could not find .djdevx/config.toml. Are you in a project managed by djdevx?"
            )
            raise typer.Exit(code=1)
        return path

    @property
    def config_data(self) -> dict:
        """Load and cache the TOML config."""
        if self._config_data is None:
            with open(self.config_path, "rb") as f:
                self._config_data = tomllib.load(f)
        return self._config_data
