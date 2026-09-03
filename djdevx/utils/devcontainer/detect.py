"""Devcontainer detection and shared dev context helpers.

These helpers let ``ddx dev`` decide between two service contexts:

* **Native (pixi)** — Postgres/Redis/OTel run as pixi-native or downloaded
  binaries bound to random persisted ports under ``.pixi/devdata/``.
* **Devcontainer (Docker)** — services are started by the devcontainer's
  ``docker-compose.yaml`` and reached via their service hostnames.

Detection mirrors the generated project's settings logic: the devcontainer
compose sets ``DEVCONTAINER`` (``base_settings.py`` ``_EnvDefaultsSource``), so
any pixi command running *inside* the container inherits it. Detection relies
**only** on that env var — presence of a ``.devcontainer/`` directory does not
imply the current shell is inside a container.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from ..project.project_structure import ProjectStructure


def in_devcontainer(project_root: Optional[Path] = None) -> bool:
    """Return True when running inside the project's devcontainer.

    True only when the ``DEVCONTAINER`` env var is set — exactly the signal the
    generated devcontainer compose propagates to pixi commands running inside
    the container. A ``.devcontainer/`` directory in the project does *not*
    imply the current shell is inside a container.
    """
    return bool(os.getenv("DEVCONTAINER"))


@dataclass
class ServiceEndpoint:
    """Connection info for a single discovered dev service."""

    name: str
    display_name: str
    host: str
    port: int
    credentials: Optional[str] = None
    url: Optional[str] = None


@dataclass
class DevelopmentContext:
    """Snapshot of the active development context for the current project."""

    in_devcontainer: bool
    services: list[ServiceEndpoint] = field(default_factory=list)
    # Rendered in the terminal from ``.devcontainer/docker-compose.yaml`` when
    # running in devcontainer mode.
    compose_path: Optional[Path] = None

    @property
    def by_name(self) -> dict[str, ServiceEndpoint]:
        return {s.name: s for s in self.services}


def read_devcontainer_services(project_root: Optional[Path] = None) -> dict[str, dict]:
    """Load services from ``.devcontainer/docker-compose.yaml``.

    Returns the raw ``services`` mapping (name → config) or an empty dict if
    the file does not exist.
    """
    root = project_root or ProjectStructure().root
    compose_path = root / ".devcontainer" / "docker-compose.yaml"
    if not compose_path.exists():
        return {}
    data = yaml.safe_load(compose_path.read_text())
    if not data:
        return {}
    return data.get("services", {})


def exported_http_port(service: dict, default: int | None = None) -> int | None:
    """Read the first host-exported HTTP port from a compose service definition.

    Compose ``ports`` entries are either a bare integer (``"5080"``) or a
    ``"HOST:CONTAINER"`` string. Return the host port when determinable,
    otherwise *default*.
    """
    ports = service.get("ports") or []
    if not ports:
        return default
    first = str(ports[0])
    # ``5080`` or ``"127.0.0.1:5080:5080"`` → host port is the piece before the
    # last ``:`` when present, otherwise the whole value.
    parts = first.split(":")
    if len(parts) == 1:
        try:
            return int(parts[0])
        except ValueError:
            return default
    try:
        return int(parts[-2])
    except (ValueError, IndexError):
        return default
