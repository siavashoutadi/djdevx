"""Dev context rendering — build the list of service endpoints to display.

Bridges the two service contexts:

* **Native (pixi)** — resolve installed py-native services (database, cache)
  and read their persisted host:port.
* **Devcontainer** — read ports/hostnames from ``.devcontainer/docker-compose.yaml``.

The result is used by ``ddx dev start``, ``ddx dev status`` and
``ddx dev credentials`` to present what is running and how to connect.
"""

from pathlib import Path
from typing import Optional

from ..utils.devcontainer.detect import (
    DevelopmentContext,
    ServiceEndpoint,
    exported_http_port,
    in_devcontainer,
    read_devcontainer_services,
)
from ..utils.project.project_structure import ProjectStructure
from ..utils.services import (
    BaseDevService,
    resolve_cache_dev_service,
    resolve_database_dev_service,
)

# Display name → compose service name for known devcontainer services.
_DEVCONTAINER_NAMES: dict[str, str] = {
    "PostgreSQL": "db",
    "Redis": "cache",
}

# Default ports when a devcontainer service defines no host export.
_DEVCONTAINER_DEFAULT_PORT: dict[str, int] = {
    "PostgreSQL": 5432,
    "Redis": 6379,
}

_DEVCONTAINER_HOST: dict[str, str] = {
    "PostgreSQL": "localhost",
    "Redis": "localhost",
}


def _native_endpoints(
    project_root: Optional[Path], verbose: bool
) -> list[ServiceEndpoint]:
    """Build endpoints for native pixi services by touching each service."""
    endpoints: list[ServiceEndpoint] = []
    services: list[BaseDevService] = [
        s
        for s in (
            resolve_database_dev_service(project_root, verbose),
            resolve_cache_dev_service(project_root, verbose),
        )
        if s is not None
    ]
    for service in services:
        creds = None
        if hasattr(service, "password") and getattr(service, "password", ""):
            creds = f"{service.dev_default_password or 'password'}"
        endpoints.append(
            ServiceEndpoint(
                name=service.name,
                display_name=service.display_name,
                host="localhost",
                port=service.port,
                credentials=creds,
                url=None,
            )
        )
    return endpoints


def _devcontainer_endpoints(project_root: Optional[Path]) -> list[ServiceEndpoint]:
    """Build endpoints from the devcontainer compose file (docker services)."""
    services = read_devcontainer_services(project_root)
    if not services:
        return []
    endpoints: list[ServiceEndpoint] = []
    for display_name, compose_name in _DEVCONTAINER_NAMES.items():
        svc = services.get(compose_name)
        if svc is None:
            continue
        port = exported_http_port(svc, _DEVCONTAINER_DEFAULT_PORT.get(display_name))
        host = _DEVCONTAINER_HOST.get(display_name, "localhost")
        endpoints.append(
            ServiceEndpoint(
                name=compose_name,
                display_name=display_name,
                host=host,
                port=port or 0,
                url=None,
            )
        )
    return endpoints


def collect_context(
    project_root: Optional[Path] = None, verbose: bool = False
) -> DevelopmentContext:
    """Return the current development context with resolved endpoints."""
    if in_devcontainer(project_root):
        root = project_root or ProjectStructure().root
        return DevelopmentContext(
            in_devcontainer=True,
            services=_devcontainer_endpoints(root),
            compose_path=root / ".devcontainer" / "docker-compose.yaml",
        )
    return DevelopmentContext(
        in_devcontainer=False,
        services=_native_endpoints(project_root, verbose),
    )
