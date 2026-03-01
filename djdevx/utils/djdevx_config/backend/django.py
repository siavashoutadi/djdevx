import typer
from pathlib import Path

from ...console.print import print_console
from ..project import ProjectConfig


class DjangoConfig(ProjectConfig):
    """
    Exposes all .djdevx paths relevant to the Django backend.
    """

    @property
    def django_backend_root(self) -> Path:
        """Root path of the Django backend project (contains pyproject.toml)."""
        backend = self.config_data.get("backend", {})
        if not backend:
            print_console.error("Backend configuration not found in djdevx config.")
            raise typer.Exit(code=1)
        if backend.get("framework") != "django":
            print_console.error("Expected 'django' backend framework in djdevx config.")
            raise typer.Exit(code=1)
        root_path = backend.get("root_path")
        if not root_path:
            print_console.error("Backend root_path not specified in djdevx config.")
            raise typer.Exit(code=1)
        return Path(root_path)
