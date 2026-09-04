"""RedisService — pixi-native local Redis dev service."""

from typing import ClassVar

from ..console.print import print_console
from .base import BaseDevService


class RedisService(BaseDevService):
    """Run Redis natively via ``redis-server``/``redis-cli`` from the pixi env."""

    name: ClassVar[str] = "redis"
    display_name: ClassVar[str] = "Redis"
    service_subdir: ClassVar[str] = "redis"
    data_subdir: ClassVar[str] = "data"
    secret_file_name: ClassVar[str] = "redis_password"
    dev_default_password: ClassVar[str] = "redis_password"
    port_env_key: ClassVar[str] = "REDIS_PORT"

    def is_up(self, step=None) -> bool:
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Checking if {self.display_name} is running..."
            )
        )
        try:
            result = self.run_pixi(
                "run",
                "redis-cli",
                "-p",
                str(self.port),
                "-a",
                self.password,
                "ping",
                timeout=15,
            )
        except OSError:
            up = False
        else:
            stdout = (
                result.stdout.decode()
                if isinstance(result.stdout, bytes)
                else (result.stdout or "")
            )
            up = result.returncode == 0 and "PONG" in stdout
        if up:
            group.ok(f"{self.display_name} is up on port {self.port}")
        else:
            group.info(f"{self.display_name} is not running")
        if step is None:
            group.done()
        return up

    def _is_ready(self) -> bool:
        """Cheap readiness probe (no CLI output) used by ``wait_until_ready``."""
        try:
            result = self.run_pixi(
                "run",
                "redis-cli",
                "-p",
                str(self.port),
                "-a",
                self.password,
                "ping",
                timeout=15,
            )
        except OSError:
            return False
        stdout = (
            result.stdout.decode()
            if isinstance(result.stdout, bytes)
            else (result.stdout or "")
        )
        return result.returncode == 0 and "PONG" in stdout

    def up(self, step=None) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.is_up(step=step):
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
            result = self.run_pixi(
                "run",
                "redis-server",
                "--port",
                str(self.port),
                "--requirepass",
                self.password,
                "--dir",
                str(self.data_dir),
                "--daemonize",
                "yes",
                "--appendonly",
                "yes",
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"redis-server failed (exit {result.returncode}): "
                    f"{result.stderr.decode().strip()}"
                )
            if not self.wait_until_ready(lambda: self._is_ready(), what="redis"):
                raise RuntimeError(
                    f"{self.display_name} did not become ready on port {self.port} "
                    f"after `redis-server --daemonize yes`"
                )
            group.ok(f"started {self.display_name.lower()} on port {self.port}")
            self._set_port_env(quiet=True)
            group.ok(f"set {self.port_env_key}={self.port}")
        finally:
            if step is None:
                group.done()

    def down(self, step=None) -> None:
        if not self.is_up(step=step):
            print_console.info(f"{self.display_name} is not running, nothing to stop")
            return
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Stopping {self.display_name}", done=f"stopped {self.display_name}"
            )
        )
        try:
            self.run_pixi(
                "run",
                "redis-cli",
                "-p",
                str(self.port),
                "-a",
                self.password,
                "shutdown",
            )
            group.ok(f"stopped {self.display_name.lower()} on port {self.port}")
        finally:
            if step is None:
                group.done()

    def reset(self, step=None) -> None:
        if not self.is_up(step=step):
            print_console.warning(f"{self.display_name} is not running, skipping flush")
            return
        group = (
            step
            if step is not None
            else print_console.step_group(
                f"Flushing {self.display_name} data",
                done=f"{self.display_name} data flushed",
            )
        )
        try:
            self.run_pixi(
                "run",
                "redis-cli",
                "-p",
                str(self.port),
                "-a",
                self.password,
                "FLUSHALL",
            )
            group.ok(f"flushed {self.display_name.lower()} data")
        finally:
            if step is None:
                group.done()
