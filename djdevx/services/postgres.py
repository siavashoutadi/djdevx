"""PostgresService — pixi-native local PostgreSQL dev service."""

from pathlib import Path
from typing import ClassVar

from ..utils.console.print import print_console
from .base import BaseDevService


class PostgresService(BaseDevService):
    """Run PostgreSQL natively via ``initdb``/``pg_ctl`` from the pixi env."""

    name: ClassVar[str] = "postgres"
    display_name: ClassVar[str] = "PostgreSQL"
    data_subdir: ClassVar[str] = "postgres"
    secret_file_name: ClassVar[str] = "postgres_password"
    dev_default_password: ClassVar[str] = "password"
    port_env_key: ClassVar[str] = "POSTGRES_PORT"
    category: ClassVar[str] = "database"

    @property
    def _log_file(self) -> Path:
        return self.service_dir / "postgres.log"

    @property
    def _pwfile(self) -> Path:
        return self.service_dir / "postgres_pwfile"

    @property
    def _initialized(self) -> bool:
        return (self.data_dir / "PG_VERSION").exists()

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
                "pg_isready",
                "-h",
                "localhost",
                "-p",
                str(self.port),
                timeout=15,
            )
        except OSError:
            up = False
        else:
            up = result.returncode == 0
        if up:
            group.ok(f"{self.display_name} is up on port {self.port}")
        else:
            group.info(f"{self.display_name} is not running")
        if step is None:
            group.done()
        return up

    def describe_down(self) -> str:
        if self._initialized and self._log_file.exists():
            return (
                f"not responding on port {self.port} — "
                f"log: {self._log_file.relative_to(self.structure.root)}"
            )
        return f"not responding on port {self.port}"

    def _is_ready(self) -> bool:
        """Cheap readiness probe (no CLI output) used by ``wait_until_ready``."""
        try:
            result = self.run_pixi(
                "run",
                "pg_isready",
                "-h",
                "localhost",
                "-p",
                str(self.port),
                timeout=15,
            )
        except OSError:
            return False
        return result.returncode == 0

    def up(self, step=None) -> None:
        self.structure.dev_data_dir.mkdir(parents=True, exist_ok=True)
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
            if not self._initialized:
                self._init_db(group)
            self._start(group)
            if not self.wait_until_ready(lambda: self._is_ready(), what="postgres"):
                raise RuntimeError(
                    f"{self.display_name} did not become ready on port {self.port} — "
                    f"check log: {self._log_file.relative_to(self.structure.root)}"
                )
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
            self.run_pixi("run", "pg_ctl", "-D", str(self.data_dir), "stop")
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
            if not self.is_up(step=group):
                group.info(f"{self.display_name} not running, skip flush")
            else:
                self.runner.run_manage_command("flush", "--noinput", check=False)
                group.ok(f"flushed {self.display_name.lower()} data")
        finally:
            if step is None:
                group.done()

    def _init_db(self, group=None) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._pwfile.write_text(self.password + "\n")
        try:
            result = self.run_pixi(
                "run",
                "initdb",
                "-D",
                str(self.data_dir),
                "-U",
                "postgres",
                f"--pwfile={self._pwfile}",
                "-A",
                "scram-sha-256",
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"initdb failed (exit {result.returncode}): "
                    f"{result.stderr.decode().strip()}"
                )
            if group is not None:
                group.ok(f"initialized {self.display_name.lower()} data directory")
        finally:
            self._pwfile.unlink(missing_ok=True)

    def _start(self, group=None) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        result = self.run_pixi(
            "run",
            "pg_ctl",
            "-D",
            str(self.data_dir),
            "-l",
            str(self._log_file),
            "-o",
            f"-p {self.port}",
            "start",
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"pg_ctl start failed (exit {result.returncode}). "
                f"Check log: {self._log_file}"
            )
        if group is not None:
            group.ok(f"started {self.display_name.lower()} on port {self.port}")
