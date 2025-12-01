import subprocess
from pathlib import Path
from typing import List, Optional

from ..djdevx_config import DjdevxConfig


class UvRunner:
    """
    Utility class for running uv commands in the Django backend root directory.
    """

    def __init__(self, backend_root: Optional[Path] = None):
        if backend_root:
            self.backend_root = backend_root
        else:
            config = DjdevxConfig()
            self.backend_root = config.django_backend_root

    def run_manage_command(
        self, command: str, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run a Django management command using uv in the backend root.

        Args:
            command: The management command name (e.g., 'startapp', 'migrate')
            *args: Additional arguments for the command
            check: Whether to raise an exception on non-zero exit code

        Returns:
            subprocess.CompletedProcess: The result of the command execution
        """
        cmd = ["uv", "run", "manage.py", command] + list(args)
        return subprocess.run(cmd, cwd=self.backend_root, check=check)

    def run_uv_command(
        self, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run a general uv command in the backend root.

        Args:
            *args: Arguments for the uv command (e.g., 'run', 'ruff', 'format', 'file.py')
            check: Whether to raise an exception on non-zero exit code

        Returns:
            subprocess.CompletedProcess: The result of the command execution
        """
        cmd = ["uv"] + list(args)
        return subprocess.run(cmd, cwd=self.backend_root, check=check)

    def add_package(
        self, package_name: str, dev: bool = False, group: str | None = None
    ) -> int:
        """
        Add a package using uv in the backend root.

        Args:
            package_name: Name of the package to add (e.g., 'django-cors-headers', 'django-anymail[resend]')
            dev: Whether to add as a dev dependency
            group: Dependency group name (if specified, takes precedence over dev flag)

        Returns:
            int: The result of the command execution
        """
        cmd = ["uv", "add", package_name]

        if group:
            cmd.extend(["--group", group])
        elif dev:
            cmd.extend(["--group", "dev"])

        return subprocess.check_call(cmd, cwd=self.backend_root)

    def remove_package(self, package_name: str, group: str | None = None) -> int:
        """
        Remove a package using uv in the backend root.

        Args:
            package_name: Name of the package to remove
            group: Dependency group name (optional)

        Returns:
            int: The result of the command execution
        """
        cmd = ["uv", "remove", package_name]

        if group:
            cmd.extend(["--group", group])

        return subprocess.check_call(cmd, cwd=self.backend_root)

    def run_command(
        self, command: List[str], check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run any command in the backend root directory.

        Args:
            command: List of command parts
            check: Whether to raise an exception on non-zero exit code

        Returns:
            subprocess.CompletedProcess: The result of the command execution
        """
        return subprocess.run(command, cwd=self.backend_root, check=check)
