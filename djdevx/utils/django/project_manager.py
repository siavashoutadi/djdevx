import re
import typer
from pathlib import Path
from typing import List, Optional

from ..djdevx_config.backend.django import DjangoConfig
from ..templates.manager import TemplateManager
from ..devcontainer import (
    ServiceConfig,
    VolumeConfig,
    DockerComposeManager,
)
from ..console.print import print_console
from .pixi_runner import PixiRunner


class DjangoProjectManager:
    """
    Complete Django project management including paths, templates, and environment.
    Centralizes all Django-specific file operations and project structure management.
    """

    def __init__(self):
        """Initialize and validate Django project."""
        self._config = DjangoConfig()
        self._template_manager = TemplateManager()
        self._devcontainer_compose = DockerComposeManager(self._config.project_root_dir)
        self._pixi_runner = PixiRunner(backend_root=self._config.django_backend_root)
        self.validate_django_project()

    def validate_django_project(self) -> None:
        """Validate that this is a Django project managed by djdevx."""
        if not self.project_path.exists():
            print_console.error(
                "Could not find project directory. Are you running from the project directory?"
            )
            raise typer.Exit(code=1)

    # Path Properties
    @property
    def pyproject_path(self) -> Path:
        """Get pyproject.toml path."""
        return Path.joinpath(self._config.django_backend_root, "pyproject.toml")

    @property
    def project_path(self) -> Path:
        """Get Django project root path."""
        return self.pyproject_path.parent

    @property
    def settings_path(self) -> Path:
        """Get settings directory path."""
        return Path.joinpath(self.project_path, "settings")

    @property
    def django_settings_path(self) -> Path:
        """Get django settings directory path."""
        return Path.joinpath(self.settings_path, "django")

    @property
    def packages_settings_path(self) -> Path:
        """Get packages settings directory path."""
        return Path.joinpath(self.settings_path, "packages")

    @property
    def urls_path(self) -> Path:
        """Get URLs directory path."""
        return Path.joinpath(self.project_path, "urls")

    @property
    def ws_urls_path(self) -> Path:
        """Get WebSocket URLs directory path."""
        return Path.joinpath(self.project_path, "ws_urls")

    @property
    def packages_urls_path(self) -> Path:
        """Get packages URLs directory path."""
        return Path.joinpath(self.urls_path, "packages")

    @property
    def base_template_path(self) -> Path:
        """Get base template path."""
        return Path.joinpath(self.project_path, "templates", "_base.html")

    @property
    def gitignore_path(self) -> Path:
        """Get .gitignore path."""
        return Path.joinpath(self.project_path, ".gitignore")

    @property
    def dockerfile_path(self) -> Path:
        """Get Dockerfile path."""
        return Path.joinpath(self.project_path, "Dockerfile")

    @property
    def static_path(self) -> Path:
        """Get static directory path."""
        return Path.joinpath(self.project_path, "static")

    @property
    def css_path(self) -> Path:
        """Get CSS directory path."""
        return Path.joinpath(self.static_path, "css")

    @property
    def js_path(self) -> Path:
        """Get JavaScript directory path."""
        return Path.joinpath(self.static_path, "js")

    # Template Operations (delegated to TemplateManager)
    def copy_templates(
        self,
        source_dir: Path,
        template_context: Optional[dict] = None,
        exclude_files: Optional[List[Path]] = None,
    ) -> None:
        """Copy template files to Django project with Jinja2 processing."""
        self._template_manager.copy_templates(
            source_dir=source_dir,
            dest_dir=self.project_path,
            template_context=template_context or {},
            exclude_files=exclude_files,
        )

    def copy_template(
        self, source_file: Path, dest_dir: Path, template_context: Optional[dict] = None
    ) -> Path:
        """Copy single template file with Jinja2 processing."""
        return self._template_manager.copy_template(
            source_file=source_file,
            dest_dir=dest_dir,
            template_context=template_context or {},
        )

    # Dependency Management
    def get_dependencies(self, group: str = "") -> list[str]:
        """Get list of dependencies via pixi list."""
        return self._pixi_runner.list_dependencies(environment=group)

    def remove_dependency(self, dependency_name: str) -> None:
        """Remove a dependency"""
        if not self.has_dependency(dependency_name):
            return

        self._pixi_runner.remove_package(dependency_name)

    def has_dependency(self, dependency_name: str, group: str = "") -> bool:
        """Check if a specific dependency is installed."""
        normalized_query = self._normalize_pkg_name(dependency_name)
        dependencies = self.get_dependencies(group)
        for dep in dependencies:
            name_without_version = (
                dep.split(">")[0]
                .split("<")[0]
                .split("=")[0]
                .split("!")[0]
                .split("~")[0]
                .strip()
            )

            name_without_extras = name_without_version.split("[")[0].strip()

            if self._normalize_pkg_name(name_without_extras) == normalized_query:
                return True
        return False

    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to the project."""
        if self.has_dependency(dependency):
            print_console.warning(f"Dependency {dependency} already exists.")
            return

        self._pixi_runner.add_package(dependency)

    @staticmethod
    def _normalize_pkg_name(name: str) -> str:
        """Normalize a package name per PEP 503 (hyphens, underscores, dots are equivalent)."""
        return re.sub(r"[-_.]+", "-", name).lower()

    def add_service_to_docker_compose(
        self,
        service_config: ServiceConfig,
        volumes: list[VolumeConfig],
    ) -> None:
        """Add a new service to docker-compose.yml."""
        self._devcontainer_compose.add_service(service_config, volumes)

    def remove_service_from_docker_compose(
        self,
        service_config: ServiceConfig,
        volumes: list[VolumeConfig],
    ) -> None:
        """Remove a service from docker-compose.yml."""
        self._devcontainer_compose.remove_service(service_config, volumes)
