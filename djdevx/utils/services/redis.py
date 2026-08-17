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

    def is_up(self) -> bool:
        print_console.step(f"Checking if {self.display_name} is running...")
        try:
            result = self.run_pixi(
                "run",
                "redis-cli",
                "-p",
                str(self.port),
                "-a",
                self.password,
                "ping",
            )
        except OSError:
            print_console.step_done(f"{self.display_name} is not running")
            return False
        stdout = (
            result.stdout.decode()
            if isinstance(result.stdout, bytes)
            else (result.stdout or "")
        )
        up = result.returncode == 0 and "PONG" in stdout
        if up:
            print_console.step_done(f"{self.display_name} is up on port {self.port}")
        else:
            print_console.step_done(f"{self.display_name} is not running")
        return up

    def up(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.is_up():
            print_console.step_done(f"{self.display_name} is already running")
            self._set_port_env()
            return
        print_console.step(f"Starting {self.display_name}...")
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
        print_console.ok(f"{self.display_name} started on port {self.port}")
        self._set_port_env()

    def down(self) -> None:
        if not self.is_up():
            print_console.step_done(
                f"{self.display_name} is not running, nothing to stop"
            )
            return
        print_console.step(f"Stopping {self.display_name}...")
        self.run_pixi(
            "run",
            "redis-cli",
            "-p",
            str(self.port),
            "-a",
            self.password,
            "shutdown",
        )
        print_console.ok(f"{self.display_name} stopped")

    def reset(self) -> None:
        if not self.is_up():
            print_console.warning(f"{self.display_name} is not running, skipping flush")
            return
        print_console.step(f"Flushing {self.display_name} data...")
        self.run_pixi(
            "run",
            "redis-cli",
            "-p",
            str(self.port),
            "-a",
            self.password,
            "FLUSHALL",
        )
        print_console.ok(f"{self.display_name} data flushed")
