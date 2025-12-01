import typer
import tomllib
from pathlib import Path

from .print_console import console


class DjdevxConfig:
    """
    Manages djdevx project configuration.
    """

    def __init__(self):
        self._config_data = None

    @property
    def config_path(self) -> Path:
        """Get path to djdevx config.toml file."""
        config_path = Path.joinpath(Path.cwd(), ".djdevx", "config.toml")
        if not config_path.exists():
            console.error(
                "Could not find .djdevx/config.toml file. Are you in a project managed by djdevx?"
            )
            raise typer.Exit(code=1)
        return config_path

    @property
    def config_data(self) -> dict:
        """Load and cache djdevx config data."""
        if self._config_data is None:
            with open(self.config_path, "rb") as config_file:
                self._config_data = tomllib.load(config_file)
        return self._config_data

    @property
    def django_backend_root(self) -> Path:
        """Get Django backend root path from config."""
        config = self.config_data
        backend_config = config.get("backend", {})
        if not backend_config:
            console.error("Backend configuration not found in djdevx config.")
            raise typer.Exit(code=1)

        backend_framework = backend_config.get("framework")
        if not backend_framework:
            console.error("Backend framework not specified in djdevx config.")
            raise typer.Exit(code=1)

        if backend_framework != "django":
            console.error(
                f"Unsupported backend framework: {backend_framework}. Expected 'django'."
            )
            raise typer.Exit(code=1)

        root_path = backend_config.get("root_path")
        if not root_path:
            console.error("Backend root_path not specified in djdevx config.")
            raise typer.Exit(code=1)
        return Path(root_path)

    @property
    def project_root_dir(self) -> Path:
        """Get project root directory (where .djdevx config is located)."""
        current_directory = Path.cwd()
        if Path.joinpath(current_directory, ".djdevx", "config.toml").exists():
            return current_directory
        console.error(
            "Is this a project managed by djdevx? Are you running from the root of your project?"
        )
        raise typer.Exit(1)

    @property
    def devcontainer_path(self) -> Path:
        """Get .devcontainer directory path."""
        return Path.joinpath(self.project_root_dir, ".devcontainer")

    @property
    def devcontainer_env_path(self) -> Path:
        """Get .devcontainer/.env directory path."""
        return Path.joinpath(self.devcontainer_path, ".env")

    @property
    def devcontainer_env_devcontainer_path(self) -> Path:
        """Get .devcontainer/.env/devcontainer file path."""
        return Path.joinpath(self.devcontainer_env_path, "devcontainer")
