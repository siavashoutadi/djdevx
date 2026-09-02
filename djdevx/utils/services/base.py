"""BaseDevService — ABC for pixi-native local development services.

Services run through ``pixi run <binary>`` via :class:`PixiRunner`. Their
data lives under ``.pixi/devdata/<provider>`` so nothing depends on Docker.
"""

import os
import socket
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, Optional

from ..console.print import print_console
from ..project.pixi_runner import PixiRunner
from ..project.project_structure import ProjectStructure


class BaseDevService(ABC):
    """Abstract local dev service (postgres, redis, ...)."""

    name: ClassVar[str] = ""
    display_name: ClassVar[str] = ""
    service_subdir: ClassVar[str] = ""
    data_subdir: ClassVar[str] = ""
    secret_file_name: ClassVar[str] = ""
    dev_default_password: ClassVar[str] = ""
    port_env_key: ClassVar[str] = ""

    def __init__(
        self, project_root: Optional[Path] = None, verbose: bool = False
    ) -> None:
        self.structure = ProjectStructure(project_root)
        self.runner = PixiRunner(self.structure.root, verbose)
        self.verbose = verbose

    @property
    def service_dir(self) -> Path:
        return self.structure.dev_data_dir / self.service_subdir

    @property
    def data_dir(self) -> Path:
        return self.service_dir / self.data_subdir

    @property
    def _port_file(self) -> Path:
        return self.service_dir / "port"

    @property
    def port(self) -> int:
        """Return the service port, generating and persisting one if needed."""
        if self._port_file.exists():
            return int(self._port_file.read_text().strip())
        port = self._generate_port()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._port_file.write_text(str(port))
        return port

    @staticmethod
    def _generate_port() -> int:
        """Ask the OS for a free port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @property
    def password(self) -> str:
        """Resolve the dev password from ``.secrets/<secret_file_name>`` or the dev default."""
        secret_path = self.structure.root / ".secrets" / self.secret_file_name
        if secret_path.exists():
            return secret_path.read_text().strip()
        return self.dev_default_password

    def _set_port_env(self, quiet: bool = False) -> None:
        """Set the service port as an environment variable for subprocesses.

        When *quiet* is True the variable is set without printing (callers
        render a ``✓ set KEY=value`` line themselves inside a step group).
        """
        if self.port_env_key:
            os.environ[self.port_env_key] = str(self.port)
            if not quiet:
                print_console.step_done(f"Set {self.port_env_key}={self.port}")

    def run_pixi(
        self, *args: str, timeout: int | None = None
    ) -> subprocess.CompletedProcess:
        return self.runner.run_pixi_command(*args, check=False, timeout=timeout)

    @abstractmethod
    def up(self, step=None) -> None:
        """Ensure the service is running (idempotent)."""

    @abstractmethod
    def down(self, step=None) -> None:
        """Stop the service if it is running."""

    @abstractmethod
    def is_up(self, step=None) -> bool:
        """Return True if the service is currently reachable."""

    def describe_down(self) -> str:
        """Return a short reason this service reports as not up."""
        return f"not responding on port {self.port}"

    @abstractmethod
    def reset(self, step=None) -> None:
        """Flush all data while keeping the service running."""

    def status(self) -> bool:
        return self.is_up()
