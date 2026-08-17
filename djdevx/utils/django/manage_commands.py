"""Helpers for running Django ``manage.py`` commands on a PixiRunner."""

import subprocess

from ..project.pixi_runner import PixiRunner


class ManageCommands:
    """Runs Django ``manage.py`` commands, delegating execution to a PixiRunner."""

    def __init__(self, runner: PixiRunner | None = None) -> None:
        self._runner = runner or PixiRunner()

    def run(
        self, command: str, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run ``manage.py <command> <args>`` via the wrapped PixiRunner."""
        return self._runner.run_manage_command(command, *args, check=check)

    def migrations_pending(self) -> bool:
        """Return True if ``manage.py migrate --check`` reports unapplied migrations."""
        result = self.run("migrate", "--check", check=False)
        return result.returncode != 0
