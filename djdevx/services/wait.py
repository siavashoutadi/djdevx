"""Shared process / port health-check helpers for pixi-native dev services.

These helpers originally lived (in private-copy form) inside
``djdevx.services.otel``. They are extracted here so any socket-based
service (Postgres, Redis, OTel collector, OpenObserve) can reuse the same
"wait until the service is actually listening" logic instead of duplicating
probe/retry code.

Public API
----------
* ``is_port_open``     — one-off TCP connect probe.
* ``is_pid_alive``     — one-off process-alive probe.
* ``read_pid``         — read a persisted pid file (or ``None``).
* ``wait_for_port``    — poll until a port opens, with crash detection.
* ``stop_process``     — SIGTERM a pid-file process and clean up the file.
"""

import os
import signal
import socket
import time
from pathlib import Path


def _pid_file(service_dir: Path) -> Path:
    return service_dir / "pid"


def pid_file(service_dir: Path) -> Path:
    """Return the persisted-pid path for a service directory."""
    return _pid_file(service_dir)


def write_pid(service_dir: Path, pid: int) -> None:
    """Persist *pid* to ``<service_dir>/pid``."""
    _pid_file(service_dir).write_text(str(pid))


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Return True if a TCP connection to ``(host, port)`` succeeds."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def is_pid_alive(pid: int) -> bool:
    """Return True if *pid* refers to a running process."""
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def read_pid(service_dir: Path) -> int | None:
    """Read a persisted pid out of ``<service_dir>/pid`` (or ``None``)."""
    path = _pid_file(service_dir)
    if not path.exists():
        return None
    try:
        return int(path.read_text().strip())
    except ValueError:
        return None


def wait_for_port(
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
        if is_port_open(host, port):
            return True
        if attempt < retries - 1:
            pid = read_pid(service_dir)
            if pid is not None and not is_pid_alive(pid):
                return False
            time.sleep(delay)
    return False


def stop_process(service_dir: Path) -> None:
    """SIGTERM the pid-file process (if any) and remove the pid file."""
    pid = read_pid(service_dir)
    if pid is None:
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except PermissionError:  # pragma: no cover - unprivileged
        pass
    _pid_file(service_dir).unlink(missing_ok=True)
