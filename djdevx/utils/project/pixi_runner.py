"""PixiRunner — simplified: runs pixi from the project root."""

import subprocess
from pathlib import Path
from typing import Optional

from ..types.pixi_types import PixiPackageSpec

from .project_structure import ProjectStructure


class PixiRunner:
    """Utility class for running pixi commands at the project root."""

    def __init__(
        self, project_root: Optional[Path] = None, verbose: bool = False
    ) -> None:
        self._verbose = verbose
        self.project_root = project_root or ProjectStructure().root

    @staticmethod
    def _extract_package_name(spec: str) -> str:
        name = spec.strip().split("[")[0]
        for i, ch in enumerate(name):
            if ch in ">=<!~;@( ":
                name = name[:i].strip()
                break
        return name

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
        run_kwargs = {"cwd": self.project_root, "check": check}
        if not self._verbose and "capture_output" not in kwargs:
            run_kwargs["capture_output"] = True
        run_kwargs.update(kwargs)
        return subprocess.run(cmd, **run_kwargs)

    def run_interactive(self, *args: str, **kwargs) -> subprocess.CompletedProcess:
        """Run a pixi command in the foreground with inherited stdio.

        Used for long-running processes (e.g. the dev server) so their output
        is streamed directly to the user's terminal.
        """
        cmd = ["pixi"] + list(args)
        return subprocess.run(cmd, cwd=self.project_root, **kwargs)

    def add_conda_package(
        self, package_name: str, feature: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        cmd_args = ["add", package_name]
        if feature:
            cmd_args.extend(["--feature", feature])
        return self.run_pixi_command(*cmd_args)

    def add_pypi_package(
        self, package_name: str, pixi_feature: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        cmd_args = ["add", "--pypi", package_name]
        if pixi_feature:
            cmd_args.extend(["--feature", pixi_feature])
        return self.run_pixi_command(*cmd_args)

    def add_package(
        self, package_name: str, feature: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        return self.add_conda_package(package_name, feature)

    def remove_conda_package(
        self, package_name: str, pixi_feature: Optional[str] = None
    ) -> Optional[subprocess.CompletedProcess]:
        cmd_args = ["remove", package_name]
        if pixi_feature:
            cmd_args.extend(["--feature", pixi_feature])
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
        return self.remove_conda_package(package_name, feature)

    def add_from_package_spec(
        self, spec: PixiPackageSpec, pixi_feature: Optional[str] = None
    ) -> None:
        if spec.kind == "pypi":
            self.add_pypi_package(spec.name, pixi_feature)
        else:
            self.add_conda_package(spec.name, pixi_feature)

    def remove_package_spec_if_exists(
        self, package_spec: PixiPackageSpec, pixi_feature: Optional[str] = None
    ) -> None:
        pkg_base = self._extract_package_name(package_spec.name)
        if package_spec.kind == "pypi":
            self.remove_pypi_package(pkg_base, feature=pixi_feature)
        else:
            self.remove_conda_package(pkg_base, pixi_feature=pixi_feature)

    def list_dependencies(self, environment: str = "") -> list[str]:
        cmd_args = ["list", "--explicit"]
        if environment:
            cmd_args.extend(["--environment", environment])
        result = self.run_pixi_command(*cmd_args, capture_output=True, text=True)
        deps: list[str] = []
        for line in result.stdout.strip().splitlines():
            stripped = line.strip()
            if (
                not stripped
                or stripped.startswith("Name")
                or stripped.startswith("Package")
            ):
                continue
            deps.append(stripped.split()[0])
        return deps

    def has_dependency(self, name: str, environment: str = "") -> bool:
        import re

        normalized = re.sub(r"[-_.]+", "-", name).lower()
        for dep in self.list_dependencies(environment):
            if re.sub(r"[-_.]+", "-", dep).lower() == normalized:
                return True
        return False
