"""BaseDevService — ABC for pixi-native local development services.

Services run through ``pixi run <binary>`` via :class:`PixiRunner`. Their
data lives under ``.pixi/devdata/<provider>`` so nothing depends on Docker.
"""

import os
import socket
import subprocess
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import ClassVar

from ..utils.console.print import print_console
from ..utils.project.pixi_runner import PixiRunner
from ..utils.project.project_structure import ProjectStructure


class _StepGroupWrapper:
    """Thin adapter so a parent *step* and a standalone group share one "done".

    Injects ``ok()``/``info()``/``warning()`` onto whatever object is wrapped so
    subclasses can call ``group.ok(...)`` uniformly whether *step* was a real
    parent step or a freshly created step group.
    """

    def __init__(self, group) -> None:
        self._group = group

    def ok(self, message: str) -> None:
        getattr(self._group, "ok", print_console.step_done)(message)

    def info(self, message: str) -> None:
        getattr(self._group, "info", print_console.info)(message)

    def warning(self, message: str) -> None:
        getattr(self._group, "warning", print_console.warning)(message)

    def done(self) -> None:
        done = getattr(self._group, "done", None)
        if done is not None:
            done()


class BaseDevService(ABC):
    """Abstract local dev service (postgres, redis, ...)."""

    name: ClassVar[str] = ""
    display_name: ClassVar[str] = ""
    service_subdir: ClassVar[str] = ""
    data_subdir: ClassVar[str] = ""
    secret_file_name: ClassVar[str] = ""
    dev_default_password: ClassVar[str] = ""
    port_env_key: ClassVar[str] = ""
    category: ClassVar[str] = ""

    def __init__(self, project_root: Path | None = None, verbose: bool = False) -> None:
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

    def _set_port_env(self, quiet: bool = False, step=None) -> None:
        """Set the service port as an environment variable for subprocesses.

        When *quiet* is True the variable is set without printing (callers
        render a ``✓ set KEY=value`` line themselves inside a step group).
        When *step* is provided, emits an indented ``✓ set KEY=value`` child.
        """
        if self.port_env_key:
            os.environ[self.port_env_key] = str(self.port)
            if step is not None:
                step.ok(f"set {self.port_env_key}={self.port}")
            elif not quiet:
                print_console.step_done(f"Set {self.port_env_key}={self.port}")

    def run_pixi(
        self, *args: str, timeout: int | None = None
    ) -> subprocess.CompletedProcess:
        return self.runner.run_pixi_command(*args, check=False, timeout=timeout)

    def _log_debug(self, message: str) -> None:
        """Surface a best-effort failure reason in verbose mode only."""
        if self.verbose:
            print_console.info(f"debug: {message}")

    def step_group(self, title: str, done: str, *, step=None):
        """Wrap the common "parent step or standalone step group" idiom.

        Returns a group object (the passed-in parent *step* if given, otherwise
        a fresh :class:`NestedStep`) so subclasses stop duplicating the
        ``step if step is not None else print_console.step_group(...)`` pattern.
        When a parent *step* is provided the returned object is used only for
        emitting ``✓`` children and is never ``done()``'d by the caller; the
        returned wrapper handles its own ``done()`` when standalone.
        """
        if step is not None:
            return step
        return _StepGroupWrapper(print_console.step_group(title, done=done))

    def wait_until_ready(
        self,
        probe: Callable[[], bool],
        *,
        retries: int = 10,
        delay: float = 0.5,
        what: str = "service",
    ) -> bool:
        """Poll *probe* (a cheap readiness check) until it is True.

        If *probe* is True within ``retries * delay`` seconds, return True.
        Otherwise return False — callers decide whether to raise/warn. This is
        the shared health-wait that Postgres/Redis/OTel use so ``up()`` only
        returns once the service is actually ready to accept connections.
        """
        for _ in range(retries):
            try:
                if probe():
                    return True
            except OSError:
                pass
            time.sleep(delay)
        return False

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

    def purge(self, step=None) -> None:
        """Stop (if running) and delete the service's data directory.

        Subclasses may override to also remove downloaded binaries etc.
        Accepts an optional parent *step* to emit ``✓`` children into.
        """
        import shutil

        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Purging {self.display_name}", done=f"purged {self.display_name}"
            )
        )
        try:
            if self.is_up():
                self.down(step=group)
            shutil.rmtree(self.service_dir, ignore_errors=True)
            group.ok(f"removed {self.display_name.lower()} data")
        finally:
            if step is None:
                group.done()
