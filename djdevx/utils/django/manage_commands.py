"""Helpers for running Django ``manage.py`` commands on a PixiRunner."""

import subprocess

from djdevx.core.process import PixiRunner


class ManageCommands:
    """Runs Django ``manage.py`` commands, delegating execution to a PixiRunner."""

    def __init__(self, runner: PixiRunner | None = None) -> None:
        self._runner = runner or PixiRunner()

    def run(
        self,
        command: str,
        *args: str,
        check: bool = True,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess:
        """Run ``manage.py <command> <args>`` via the wrapped PixiRunner."""
        return self._runner.run_manage_command(
            command, *args, check=check, timeout=timeout
        )

    def migrations_pending(self) -> bool | None:
        """Return True if ``manage.py migrate --check`` reports unapplied migrations.

        Returns ``None`` if the check could not complete (e.g. it timed out trying
        to reach a database that is down).
        """
        try:
            result = self.run("migrate", "--check", check=False, timeout=15)
        except subprocess.TimeoutExpired:
            return None
        return result.returncode != 0
