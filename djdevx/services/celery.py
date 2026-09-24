"""CeleryWorkerService and CeleryBeatService — pixi-native daemon dev services.

Both run the ``celery`` CLI via ``pixi run`` in the background with a PID
file under ``.pixi/devdata/`` so ``ddx dev start``/``up`` can bring them up
and ``ddx dev down``/``status`` can stop/monitor them. Unlike socket-based
services (postgres/redis/otel) they expose no TCP port: liveness is judged
by whether the recorded PID is still running.
"""

from pathlib import Path
from typing import ClassVar

from djdevx.core.console import print_console
from djdevx.core.process import is_pid_alive, read_pid, stop_process, write_pid

from .base import BaseDevService


class _CeleryDaemon(BaseDevService):
    """Shared background-daemon behavior for the Celery worker and Beat."""

    celery_subcommand: ClassVar[str] = ""
    service_subdir: ClassVar[str] = ""
    category: ClassVar[str] = ""
    port_env_key: ClassVar[str] = ""
    secret_file_name: ClassVar[str] = ""
    dev_default_password: ClassVar[str] = ""
    data_subdir: ClassVar[str] = ""

    @property
    def _log_file(self) -> Path:
        return self.service_dir / f"{self.name}.log"

    def _command(self) -> list[str]:
        return [
            "run",
            "celery",
            "-A",
            "applications.celery",
            self.celery_subcommand,
            "--loglevel=info",
        ]

    def is_up(self, step=None) -> bool:
        pid = read_pid(self.service_dir)
        up = pid is not None and is_pid_alive(pid)
        if step is not None:
            if up:
                step.ok(f"{self.display_name} is up")
            else:
                step.info(f"{self.display_name} is not running")
        return up

    def describe_down(self) -> str:
        pid = read_pid(self.service_dir)
        if pid is None:
            return "no pid file — the daemon was never started"
        return "process exited (pid file present but not running)"

    def _launch_background(self, command: list[str]) -> None:
        import subprocess

        self.service_dir.mkdir(parents=True, exist_ok=True)
        with self._log_file.open("ab") as f:
            proc = subprocess.Popen(
                ["pixi", *command],
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=self.structure.root,
                env=self._daemon_env(),
            )
        write_pid(self.service_dir, proc.pid)

    def _daemon_env(self) -> dict:
        import os

        # Let the daemon inherit the current process env so Redis port
        # variables (set by the cache service) reach the worker settings.
        return os.environ.copy()

    def up(self, step=None) -> None:
        if self.is_up():
            print_console.step_done(f"{self.display_name} is already running")
            return
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Starting {self.display_name}", done=f"started {self.display_name}"
            )
        )
        try:
            self._launch_background(self._command())
            # No TCP port to probe; wait briefly to catch an immediate crash.
            alive = self.wait_until_ready(
                lambda: self.is_up(), retries=6, delay=0.5, what=self.name
            )
            if alive:
                group.ok(f"{self.display_name.lower()} started")
            else:
                print_console.warning(
                    f"{self.display_name} launched but stopped — "
                    f"check {self._log_file.relative_to(self.structure.root)}"
                )
        finally:
            if step is None:
                group.done()

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
            stop_process(self.service_dir)
            group.ok(f"stopped {self.display_name.lower()}")
        finally:
            if step is None:
                group.done()

    def reset(self, step=None) -> None:
        print_console.step_done(f"{self.display_name} has no persistent data to flush")

    def status(self) -> bool:
        return self.is_up()


class CeleryWorkerService(_CeleryDaemon):
    """Run a Celery worker via the pixi env in the background."""

    name: ClassVar[str] = "celery"
    display_name: ClassVar[str] = "Celery Worker"
    celery_subcommand: ClassVar[str] = "worker"
    service_subdir: ClassVar[str] = "celery/worker"
    category: ClassVar[str] = "task-queue"


class CeleryBeatService(_CeleryDaemon):
    """Run Celery Beat via the pixi env in the background."""

    name: ClassVar[str] = "celery-beat"
    display_name: ClassVar[str] = "Celery Beat"
    celery_subcommand: ClassVar[str] = "beat"
    service_subdir: ClassVar[str] = "celery/beat"
    category: ClassVar[str] = "scheduler"
