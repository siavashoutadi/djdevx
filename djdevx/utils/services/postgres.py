"""PostgresService — pixi-native local PostgreSQL dev service."""

from pathlib import Path
from typing import ClassVar

from ..console.print import print_console
from .base import BaseDevService


class PostgresService(BaseDevService):
    """Run PostgreSQL natively via ``initdb``/``pg_ctl`` from the pixi env."""

    name: ClassVar[str] = "postgres"
    display_name: ClassVar[str] = "PostgreSQL"
    data_subdir: ClassVar[str] = "postgres"
    secret_file_name: ClassVar[str] = "postgres_password"
    dev_default_password: ClassVar[str] = "password"
    port_env_key: ClassVar[str] = "POSTGRES_PORT"

    @property
    def _log_file(self) -> Path:
        return self.service_dir / "postgres.log"

    @property
    def _pwfile(self) -> Path:
        return self.service_dir / "postgres_pwfile"

    @property
    def _initialized(self) -> bool:
        return (self.data_dir / "PG_VERSION").exists()

    def is_up(self) -> bool:
        print_console.step(f"Checking if {self.display_name} is running...")
        try:
            result = self.run_pixi(
                "run", "pg_isready", "-h", "localhost", "-p", str(self.port)
            )
        except OSError:
            print_console.step_done(f"{self.display_name} is not running")
            return False
        up = result.returncode == 0
        if up:
            print_console.step_done(f"{self.display_name} is up on port {self.port}")
        else:
            print_console.step_done(f"{self.display_name} is not running")
        return up

    def up(self) -> None:
        self.structure.dev_data_dir.mkdir(parents=True, exist_ok=True)
        if not self._initialized:
            self._init_db()
        if not self.is_up():
            self._start()
        else:
            print_console.step_done(f"{self.display_name} is already running")
        self._set_port_env()

    def down(self) -> None:
        if not self.is_up():
            print_console.step_done(
                f"{self.display_name} is not running, nothing to stop"
            )
            return
        print_console.step(f"Stopping {self.display_name}...")
        self.run_pixi("run", "pg_ctl", "-D", str(self.data_dir), "stop")
        print_console.ok(f"{self.display_name} stopped")

    def reset(self) -> None:
        print_console.step(f"Flushing {self.display_name} data...")
        self.runner.run_manage_command("flush", "--noinput", check=False)
        print_console.ok(f"{self.display_name} data flushed")

    def _init_db(self) -> None:
        print_console.step(f"Initializing {self.display_name} data directory...")
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
            print_console.ok(f"{self.display_name} data initialized")
        finally:
            self._pwfile.unlink(missing_ok=True)

    def _start(self) -> None:
        print_console.step(f"Starting {self.display_name} server...")
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
        print_console.ok(f"{self.display_name} server started on port {self.port}")
