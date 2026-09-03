"""OtelCollectorService and OpenObserveService — pixi-native observability dev services.

Both run as binaries on a random persisted port under ``.pixi/devdata/`` and are
daemonized with a PID file so ``ddx dev up``/``start`` can start them in the
background and ``ddx dev down`` can stop them:

* **OtelCollectorService** runs the ``otelcol`` binary (from the pixi env, or
  falling back to an on-PATH binary) with a rendered collector config.
* **OpenObserveService** downloads the OpenObserve static binary into
  ``.pixi/devdata/bin/`` and runs it as a local telemetry backend.

Ports are pushed into ``os.environ`` via ``port_env_key`` so generated
settings (``OTEL_COLLECTOR_PORT``, ``OPENOBSERVE_PORT``) resolve correctly,
mirroring how Postgres/Redis inject ``POSTGRES_PORT``/``REDIS_PORT``.
"""

import os
import signal
import socket
import subprocess
import time
from pathlib import Path
from typing import ClassVar, Optional

from ..console.print import print_console
from ..tracking import ProjectTracking
from . import binary
from .base import BaseDevService

# Default OpenObserve bootstrap credentials (match the devcontainer image).
OPENOBSERVE_DEFAULT_EMAIL = "admin@example.com"
OPENOBSERVE_DEFAULT_PASSWORD = "ZoAdmin123!"


def _pid_file(service_dir: Path) -> Path:
    return service_dir / "pid"


def _is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _is_pid_alive(pid: int) -> bool:
    """Return True if *pid* refers to a running process."""
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _wait_for_port(
    host: str,
    port: int,
    service_dir: Path,
    *,
    retries: int = 5,
    delay: float = 1.0,
) -> bool:
    """Poll until *port* is open or *retries* probes are exhausted.

    Used after ``Popen`` to give a socket-based service time to bind its port.
    If the port is closed **and** the stored PID is dead the service has
    crashed — no retry will help, so False is returned immediately.
    """
    for attempt in range(retries):
        if _is_port_open(host, port):
            return True
        if attempt < retries - 1:
            pid = _read_pid(service_dir)
            if pid is not None and not _is_pid_alive(pid):
                return False
            time.sleep(delay)
    return False


def _read_pid(service_dir: Path) -> Optional[int]:
    path = _pid_file(service_dir)
    if not path.exists():
        return None
    try:
        return int(path.read_text().strip())
    except ValueError:
        return None


def _describe_down_port(service: "BaseDevService") -> str:
    """Explain why a socket-based service is not up, from its port + pid state."""
    pid = _read_pid(service.service_dir)
    if pid is None:
        reason = "no pid file — the service was never started"
    elif not _is_pid_alive(pid):
        reason = f"process exited (pid {pid} no longer running)"
    else:
        reason = f"process running but not listening on port {service.port}"
    log = service._log_file if hasattr(service, "_log_file") else None
    if log is not None and log.exists():
        reason = f"{reason} — log: {log.relative_to(service.structure.root)}"
    return reason


def _report_launch_warning(service: "BaseDevService", *, port: int) -> None:
    """Warn that a launched process never started listening on its port."""
    log = service._log_file if hasattr(service, "_log_file") else None
    hint = f" — check {log}" if log is not None else ""
    print_console.warning(
        f"{service.display_name} launched but is not listening on port {port} yet{hint}"
    )


def _stop_process(service_dir: Path) -> None:
    pid = _read_pid(service_dir)
    if pid is None:
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except PermissionError:  # pragma: no cover - unprivileged
        pass
    _pid_file(service_dir).unlink(missing_ok=True)


class OtelCollectorService(BaseDevService):
    """Run the OpenTelemetry collector natively via a downloaded ``otelcol-contrib`` binary."""

    name: ClassVar[str] = "otel"
    display_name: ClassVar[str] = "OTel Collector"
    service_subdir: ClassVar[str] = "otel"
    data_subdir: ClassVar[str] = "data"
    secret_file_name: ClassVar[str] = "otel_password"
    dev_default_password: ClassVar[str] = ""
    port_env_key: ClassVar[str] = "OTEL_COLLECTOR_PORT"

    def __init__(
        self, project_root: Optional[Path] = None, verbose: bool = False
    ) -> None:
        super().__init__(project_root, verbose)
        self.bin_dir = self.structure.root / ".pixi" / "devdata" / "bin"
        self.binary_path: Optional[Path] = None

    @property
    def config_path(self) -> Path:
        return self.service_dir / "otel-collector-config.yaml"

    @property
    def _log_file(self) -> Path:
        return self.service_dir / "collector.log"

    def _project_name(self) -> str:
        try:
            tracking = ProjectTracking(self.structure.root)
            name = tracking.get_config().get("project_name")
            if name:
                return name
        except Exception:  # noqa: BLE001 - best-effort
            pass
        return self.structure.root.name

    def _discover_openobserve_base(self) -> str:
        """Return the base URL of a running local OpenObserve (defaults to 5080)."""
        try:
            from .resolver import resolve_openobserve_dev_service

            observe = resolve_openobserve_dev_service(project_root=self.structure.root)
            if observe is not None and observe.is_up():
                return f"http://localhost:{observe.port}"
        except Exception:  # noqa: BLE001 - best-effort
            pass
        return "http://localhost:5080"

    def _ensure_config(self, step=None) -> None:
        from ...features.otel.collector_config import build_collector_config

        self.service_dir.mkdir(parents=True, exist_ok=True)
        rendered = build_collector_config(
            project_name=self._project_name(),
            otlp_endpoint=f"0.0.0.0:{self.port}",
            openobserve_base_url=self._discover_openobserve_base(),
        )
        if step is not None and not (
            self.config_path.exists() and self.config_path.read_text() == rendered
        ):
            step.ok("wrote otel collector config")
        self.config_path.write_text(rendered)

    def _binary_command(self) -> list[str]:
        return [str(self.binary_path), "--config", str(self.config_path)]

    def is_up(self) -> bool:
        return _is_port_open("localhost", self.port)

    def describe_down(self) -> str:
        return _describe_down_port(self)

    def up(self, step=None) -> None:
        if self.is_up():
            print_console.step_done(f"{self.display_name} is already running")
            self._set_port_env(quiet=True)
            return
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Starting {self.display_name}", done=f"started {self.display_name}"
            )
        )
        try:
            self._ensure_config(group)
            binary_path = self._ensure_binary(group)
            if binary_path is None:
                return
            self.binary_path = binary_path
            self._launch_background(self._binary_command(), self._log_file)
            if _wait_for_port("localhost", self.port, self.service_dir):
                group.ok(f"started {self.display_name.lower()} on port {self.port}")
            else:
                _report_launch_warning(self, port=self.port)
            self._set_port_env(quiet=True)
            group.ok(f"set {self.port_env_key}={self.port}")
        finally:
            if step is None:
                group.done()

    def _ensure_binary(self, step=None) -> Optional[Path]:
        if self.binary_path is not None and self.binary_path.exists():
            return self.binary_path
        # Prefer an existing downloaded binary, then an on-PATH otelcol.
        existing = [
            p
            for p in self.bin_dir.glob("otelcol*")
            if p.is_file() and not p.name.endswith((".md", ".txt"))
        ]
        if existing:
            if step is not None:
                step.ok(f"found {self.display_name.lower()} binary")
            return existing[0]
        on_path = self._command_on_path("otelcol") or self._command_on_path(
            "otelcol-contrib"
        )
        if on_path:
            if step is not None:
                step.ok(f"found {self.display_name.lower()} binary on PATH")
            return Path(on_path)
        if step is not None:
            step.ok(f"downloaded {self.display_name.lower()} binary")
        result = binary.download_and_extract(
            binary.otelcol_contrib_release_url(),
            self.bin_dir,
            binary_glob="otelcol*",
        )
        if result is None:
            print_console.fail(f"Failed to download {self.display_name} binary.")
            return None
        return result

    @staticmethod
    def _command_on_path(name: str) -> str | None:
        import shutil

        return shutil.which(name)

    def _launch_background(self, command: list[str], log: Path) -> None:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("ab") as f:
            proc = subprocess.Popen(
                command,
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=self.structure.root,
            )
        _pid_file(self.service_dir).write_text(str(proc.pid))

    def down(self, step=None) -> None:
        if not self.is_up():
            print_console.step_done(
                f"{self.display_name} is not running, nothing to stop"
            )
            return
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Stopping {self.display_name}", done=f"stopped {self.display_name}"
            )
        )
        try:
            _stop_process(self.service_dir)
            group.ok(f"stopped {self.display_name.lower()} on port {self.port}")
        finally:
            if step is None:
                group.done()

    def reset(self, step=None) -> None:
        print_console.step_done(f"{self.display_name} has no persistent data to flush")


class OpenObserveService(BaseDevService):
    """Run OpenObserve natively from a downloaded binary in ``.pixi/devdata/bin``."""

    name: ClassVar[str] = "openobserve"
    display_name: ClassVar[str] = "OpenObserve"
    service_subdir: ClassVar[str] = "openobserve"
    data_subdir: ClassVar[str] = "data"
    secret_file_name: ClassVar[str] = "openobserve_password"
    dev_default_password: ClassVar[str] = OPENOBSERVE_DEFAULT_PASSWORD
    port_env_key: ClassVar[str] = "OPENOBSERVE_PORT"

    def __init__(
        self, project_root: Optional[Path] = None, verbose: bool = False
    ) -> None:
        super().__init__(project_root, verbose)
        self.bin_dir = self.structure.root / ".pixi" / "devdata" / "bin"
        self.binary_path: Optional[Path] = None

    @property
    def data_dir(self) -> Path:
        return self.service_dir / self.data_subdir

    @property
    def _log_file(self) -> Path:
        return self.service_dir / "openobserve.log"

    def _root_user_email(self) -> str:
        secret_path = self.structure.root / ".secrets" / "openobserve_email"
        if secret_path.exists():
            return secret_path.read_text().strip()
        return OPENOBSERVE_DEFAULT_EMAIL

    def _ensure_binary(self, step=None) -> Optional[Path]:
        if self.binary_path is not None and self.binary_path.exists():
            return self.binary_path
        existing = list(self.bin_dir.glob("openobserve*"))
        if existing:
            self.binary_path = existing[0]
            if step is not None:
                step.ok(f"found {self.display_name.lower()} binary")
            return self.binary_path
        if step is not None:
            step.ok(f"downloaded {self.display_name.lower()} binary")
        result = binary.download_and_extract(
            binary.openobserve_release_url(),
            self.bin_dir,
            binary_glob="openobserve*",
            archive_type="zip" if self._os_name() == "windows" else "tar.gz",
        )
        if result is None:
            print_console.fail(f"Failed to download {self.display_name} binary.")
            return None
        self.binary_path = result
        return result

    @staticmethod
    def _os_name() -> str:
        return binary._os_name()

    def is_up(self) -> bool:
        return _is_port_open("localhost", self.port)

    def describe_down(self) -> str:
        return _describe_down_port(self)

    def up(self, step=None) -> None:
        if self.is_up():
            print_console.step_done(f"{self.display_name} is already running")
            self._set_port_env(quiet=True)
            return
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Starting {self.display_name}", done=f"started {self.display_name}"
            )
        )
        try:
            binary_path = self._ensure_binary(group)
            if binary_path is None:
                return
            self.service_dir.mkdir(parents=True, exist_ok=True)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            command = [
                str(binary_path),
                "--local-mode",
                "--data",
                str(self.data_dir),
                "--http-port",
                str(self.port),
                "--username",
                self._root_user_email(),
                "--password",
                self.password,
            ]
            self._launch_background(command, self._log_file)
            if _wait_for_port("localhost", self.port, self.service_dir):
                group.ok(f"started {self.display_name.lower()} on port {self.port}")
            else:
                _report_launch_warning(self, port=self.port)
            self._set_port_env(quiet=True)
            group.ok(f"set {self.port_env_key}={self.port}")
            group.info(
                "OpenObserve is ready — see `ddx dev credentials` for the URL and login"
            )
        finally:
            if step is None:
                group.done()

    def _launch_background(self, command: list[str], log: Path) -> None:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("ab") as f:
            proc = subprocess.Popen(
                command,
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=self.data_dir,
            )
        _pid_file(self.service_dir).write_text(str(proc.pid))

    def down(self, step=None) -> None:
        if not self.is_up():
            print_console.step_done(
                f"{self.display_name} is not running, nothing to stop"
            )
            return
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Stopping {self.display_name}", done=f"stopped {self.display_name}"
            )
        )
        try:
            _stop_process(self.service_dir)
            group.ok(f"stopped {self.display_name.lower()} on port {self.port}")
        finally:
            if step is None:
                group.done()

    def reset(self, step=None) -> None:
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Flushing {self.display_name} data",
                done=f"{self.display_name} data flushed",
            )
        )
        try:
            import shutil as _shutil

            _shutil.rmtree(self.data_dir, ignore_errors=True)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            group.ok(f"removed {self.display_name.lower()} data")
        finally:
            if step is None:
                group.done()

    def purge(self, step=None) -> None:
        import shutil as _shutil

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
            _shutil.rmtree(self.service_dir, ignore_errors=True)
            group.ok(f"removed {self.display_name.lower()} data")
            for b in self.bin_dir.glob("openobserve*"):
                b.unlink(missing_ok=True)
            group.ok("removed downloaded openobserve binaries")
        finally:
            if step is None:
                group.done()
