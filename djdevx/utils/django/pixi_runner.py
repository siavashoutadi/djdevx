import json
import re
import subprocess
from pathlib import Path
from typing import List, Optional

from ..djdevx_config.backend.django import DjangoConfig
from ...utils.console.print import print_console


class PixiRunner:
    """
    Utility class for running pixi commands in the Django backend root directory.
    """

    def __init__(self, backend_root: Optional[Path] = None):
        if backend_root:
            self.backend_root = backend_root
        else:
            config = DjangoConfig()
            self.backend_root = config.django_backend_root

    def run_manage_command(
        self, command: str, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess:
        return self.run_pixi_command(
            "run", "python", "manage.py", command, *args, check=check
        )

    def run_pixi_command(
        self, *args: str, check: bool = True, **kwargs
    ) -> subprocess.CompletedProcess:
        cmd = ["pixi"] + list(args)
        print_console.step(f"Running: {' '.join(cmd)}")
        run_kwargs = {"cwd": self.backend_root, "check": check}
        run_kwargs.update(kwargs)
        return subprocess.run(cmd, **run_kwargs)

    @staticmethod
    def _extract_package_name(spec: str) -> str:
        """Extract bare package name from a dependency spec.

        'django~=5.0' -> 'django'
        'requests[security]' -> 'requests'
        """
        name = spec.strip().split("[")[0]
        for i, ch in enumerate(name):
            if ch in ">=<!~;@( ":
                name = name[:i].strip()
                break
        return name

    def _exists_in_conda(self, package_name: str) -> bool:
        """Check if a package exists on conda-forge via ``pixi search``."""
        name = self._extract_package_name(package_name)
        result = self.run_pixi_command(
            "search",
            "--limit",
            "1",
            name,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _find_installed_source(
        self, package_name: str, environment: Optional[str] = None
    ) -> Optional[str]:
        """Determine whether an installed package is from conda or pypi.

        Uses ``pixi list --json`` and inspects the ``kind`` field.
        Names are normalized per PEP 503 before comparison because pixi
        stores pypi package names with underscores but may receive
        hyphenated names.

        Returns ``"conda"``, ``"pypi"``, or ``None`` if not installed.
        """
        name = self._extract_package_name(package_name)
        cmd_args = ["list", "--json"]
        if environment:
            cmd_args.extend(["--environment", environment])
        result = self.run_pixi_command(
            *cmd_args, check=False, capture_output=True, text=True
        )
        if result.returncode != 0:
            return None
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return None
        normalized_name = self._normalize_pkg_name(name)
        for pkg in data:
            if isinstance(pkg, dict):
                pkg_normalized = self._normalize_pkg_name(pkg.get("name", ""))
                if pkg_normalized == normalized_name:
                    return pkg.get("kind")
        return None

    @staticmethod
    def _normalize_pkg_name(name: str) -> str:
        """Normalize a package name per PEP 503."""
        return re.sub(r"[-_.]+", "-", name).lower()

    def add_conda_package(
        self, package_name: str, feature: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        cmd_args = ["add", package_name]
        if feature:
            cmd_args.extend(["--feature", feature])
        return self.run_pixi_command(*cmd_args)

    def add_pypi_package(
        self, package_name: str, feature: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        cmd_args = ["add", "--pypi", package_name]
        if feature:
            cmd_args.extend(["--feature", feature])
        return self.run_pixi_command(*cmd_args)

    def add_package(
        self, package_name: str, feature: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        if "[" in package_name:
            return self.add_pypi_package(package_name, feature)

        if self._exists_in_conda(package_name):
            return self.add_conda_package(package_name, feature)

        try:
            return self.add_pypi_package(package_name, feature)
        except subprocess.CalledProcessError:
            raise RuntimeError(
                f"Package '{package_name}' not found in conda or pypi"
            ) from None

    def remove_conda_package(
        self, package_name: str, feature: Optional[str] = None
    ) -> Optional[subprocess.CompletedProcess]:
        cmd_args = ["remove", package_name]
        if feature:
            cmd_args.extend(["--feature", feature])
        try:
            return self.run_pixi_command(*cmd_args)
        except subprocess.CalledProcessError:
            return None

    def remove_pypi_package(
        self, package_name: str, feature: Optional[str] = None
    ) -> Optional[subprocess.CompletedProcess]:
        cmd_args = ["remove", "--pypi", package_name]
        if feature:
            cmd_args.extend(["--feature", feature])
        try:
            return self.run_pixi_command(*cmd_args)
        except subprocess.CalledProcessError:
            return None

    def remove_package(
        self, package_name: str, feature: Optional[str] = None
    ) -> Optional[subprocess.CompletedProcess]:
        source = self._find_installed_source(package_name, environment=feature)
        if source == "conda":
            return self.remove_conda_package(package_name, feature)
        elif source == "pypi":
            return self.remove_pypi_package(package_name, feature)
        return None

    def list_dependencies(self, environment: str = "") -> list[str]:
        """Run pixi list and return parsed package names.

        Args:
            environment: Optional environment/feature name (e.g. 'dev').

        Returns:
            A list of explicitly declared package names (without version specifiers).
        """
        cmd_args = ["list", "--explicit"]
        if environment:
            cmd_args.extend(["--environment", environment])
        result = self.run_pixi_command(*cmd_args, capture_output=True, text=True)
        deps: list[str] = []
        for line in result.stdout.strip().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("Package"):
                continue
            deps.append(stripped.split()[0])
        return deps

    def run_command(
        self, command: List[str], check: bool = True
    ) -> subprocess.CompletedProcess:
        return subprocess.run(command, cwd=self.backend_root, check=check)
