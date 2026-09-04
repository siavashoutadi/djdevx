"""Docker Compose YAML manager for services and volumes."""

import yaml
from pathlib import Path
from typing import Any
from typing import TypedDict, NotRequired

from djdevx.core.console import NestedStep, print_console


class ServiceConfig(TypedDict):
    name: str
    image: str
    environment: NotRequired[dict[str, str]]
    env_file: NotRequired[list[str]]
    volumes: NotRequired[list[str]]
    networks: NotRequired[list[str]]
    ports: NotRequired[list[str]]
    command: NotRequired[str]
    depends_on: NotRequired[list[str]]


class VolumeConfig(TypedDict):
    name: str
    driver: NotRequired[str]


class DockerComposeManager:
    """Manage docker-compose.yaml services and volumes."""

    def __init__(self, project_root: Path):
        """Initialize the docker-compose manager.

        Args:
            project_root: Root directory of the project.
        """
        self.compose_path = project_root / ".devcontainer" / "docker-compose.yaml"
        self.compose_data = self._load_compose()

    def _load_compose(self) -> dict:
        """Load docker-compose.yaml file."""
        if not self.compose_path.exists():
            self.compose_path.parent.mkdir(parents=True, exist_ok=True)
            self.compose_data = {}
            self._save_compose()
            return {}

        with open(self.compose_path, "r") as f:
            data = yaml.safe_load(f)
        return data if data else {}

    def _save_compose(self) -> None:
        """Save docker-compose.yaml file."""
        with open(self.compose_path, "w") as f:
            yaml.dump(
                self.compose_data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                indent=2,
                line_break="\n",
            )

    def add_service(
        self,
        service: ServiceConfig,
        volumes: list[VolumeConfig],
        step: NestedStep | None = None,
    ) -> None:
        """Add a service to docker-compose.yaml.

        Args:
            service: Dictionary containing the service configuration.
            volumes: List containing the volume configuration.
            step: Optional parent NestedStep to emit an indented ``✓`` child into.
        """
        service_name = service.get("name")
        if "services" not in self.compose_data:
            self.compose_data["services"] = {}
        self.compose_data["services"][service_name] = {
            key: value for key, value in service.items() if key != "name"
        }

        if volumes:
            if "volumes" not in self.compose_data:
                self.compose_data["volumes"] = {}
            for volume in volumes:
                volume_name = volume.get("name")
                self.compose_data["volumes"][volume_name] = {
                    key: value for key, value in volume.items() if key != "name"
                }

        self._save_compose()
        message = (
            f"Added service '{service_name}' to docker-compose.yaml for devcontainer"
        )
        if step is not None:
            step.ok(message)
        else:
            print_console.ok(message)

    def remove_service(
        self,
        service: ServiceConfig,
        volumes: list[VolumeConfig],
        step: NestedStep | None = None,
    ) -> None:
        """Remove a service from docker-compose.yaml.

        Args:
            service: Dictionary containing the service configuration.
            volumes: List containing the volume configuration.
            step: Optional parent NestedStep to emit an indented ``✓`` child into.
        """
        service_name = service.get("name")
        volume_keys = [volume.get("name") for volume in volumes]

        if service_name in self.compose_data["services"]:
            del self.compose_data["services"][service_name]

        if volume_keys:
            if "volumes" in self.compose_data:
                for volume_key in volume_keys:
                    if volume_key in self.compose_data["volumes"]:
                        del self.compose_data["volumes"][volume_key]

        self._save_compose()
        message = f"Removed service '{service_name}' from docker-compose.yaml for devcontainer"
        if step is not None:
            step.ok(message)
        else:
            print_console.ok(message)

    def service_exists(self, service_name: str) -> bool:
        """Check if a service exists in docker-compose.yaml.

        Args:
            service_name: Name of the service to check.

        Returns:
            True if the service exists, False otherwise.
        """
        return service_name in self.compose_data.get("services", {})

    def get_service(self, service_name: str) -> dict[str, Any] | None:
        """Get service configuration from docker-compose.yaml.

        Args:
            service_name: Name of the service to retrieve.

        Returns:
            Service configuration dictionary or None if not found.
        """
        return self.compose_data.get("services", {}).get(service_name)
