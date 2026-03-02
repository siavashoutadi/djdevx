"""BasePackage class for standardized Django package installation management."""

import functools
import shutil
from pathlib import Path
from typing import Any, Callable, Optional

import typer

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager
from ....utils.django.uv_runner import UvRunner
from ....utils.templates.manager import TemplateManager


class PathDeriver:
    """
    Derives package configuration paths from file location.

    Handles auto-derivation of settings_file, url_file, and template_path
    for both root packages (packages/name.py) and sub-packages (packages/dir/name.py).
    """

    def __init__(self, file_path: Path) -> None:
        """
        Initialize path deriver.

        Args:
            file_path: Absolute path to the package file
        """
        self.file_path = file_path.resolve()
        self.file_stem = file_path.stem
        self.parent_dir = file_path.parent
        self.parent_name = file_path.parent.name

    def _derive_filename(self, override: Optional[str]) -> str:
        """
        Auto-derive filename (settings or URL).

        If override is set, returns it. Otherwise:
        - Root packages (packages/name.py) → name.py
        - Sub-packages (packages/dir/name.py) → dir_name.py
        """
        if override is not None:
            return override
        return (
            f"{self.file_stem}.py"
            if self.parent_name == "packages"
            else f"{self.parent_name}_{self.file_stem}.py"
        )

    def derive_settings_file(self, override: Optional[str]) -> str:
        """
        Auto-derive settings filename.

        If override is set, returns it. Otherwise:
        - Root packages (packages/name.py) → name.py
        - Sub-packages (packages/dir/name.py) → dir_name.py
        """
        return self._derive_filename(override)

    def derive_url_file(self, override: Optional[str]) -> str:
        """
        Auto-derive URL filename (same rule as settings_file).

        If override is set, returns it. Otherwise:
        - Root packages (packages/name.py) → name.py
        - Sub-packages (packages/dir/name.py) → dir_name.py
        """
        return self._derive_filename(override)

    def derive_template_path(self, override: Optional[str]) -> str:
        """
        Auto-derive template path from file relative to packages directory.

        If override is set, returns it. Otherwise:
        - Root packages (packages/name.py) → name
        - Sub-packages (packages/dir/name.py) → dir/name
        """
        if override is not None:
            return override
        # Find the packages directory by walking up from the file
        current = self.file_path.parent
        while current.name != "packages" and current != current.parent:
            current = current.parent
        # Get path relative to packages directory (without .py extension)
        return str(self.file_path.relative_to(current).with_suffix(""))

    def derive_ws_url_dirs(self, override: Optional[str]) -> str:
        """Auto-derive WebSocket URL directory from file name.

        If override is set, returns it. Otherwise uses the same logic as derive_url_file
        but without the .py extension.
        """
        filename = self._derive_filename(override)
        return filename.replace(".py", "")


class BasePackage:
    """
    Base class for Django packages with auto-registered install/remove/env commands.

    Subclasses declare class-level config (name, packages, dev_packages, etc.)
    and override methods only for custom logic. The `app` property automatically
    wraps commands with step/success prints via functools.wraps.

    Auto-derivation from __file__:
    - settings_file: stem of the file (whitenoise.py → whitenoise.py)
    - url_file: stem of the file (django_debug_toolbar.py → django_debug_toolbar.py)
    - template_path: relative path from packages/ directory

    For sub-packages (e.g., packages/django_storages/s3.py):
    - settings_file: parent_name + '_' + stem (django_storages_s3.py)
    - url_file: parent_name + '_' + stem (django_storages_s3.py)
    - template_path: relative path from packages/ (django_storages/s3)
    """

    # Class-level config attributes (all optional, subclasses override as needed)
    name: str = ""
    packages: list[str] = []
    dev_packages: list[str] = []
    ws_url_dirs: Optional[str] = None
    env_vars: dict[str, str] = {}
    settings_file: Optional[str] = None
    url_file: Optional[str] = None
    template_path: Optional[str] = None

    def __init__(self, file: str) -> None:
        """
        Initialize BasePackage with auto-derivation of paths.

        Args:
            file: __file__ from the subclass
        """
        file_path = Path(file).resolve()
        self._file_path = file_path
        self._djdevx_root_cache: Optional[Path] = None

        deriver = PathDeriver(file_path)
        self._settings_file = deriver.derive_settings_file(self.settings_file)
        self._url_file = deriver.derive_url_file(self.url_file)
        self._template_path = deriver.derive_template_path(self.template_path)
        self._ws_url_dirs = deriver.derive_ws_url_dirs(self.ws_url_dirs)

        self._pm: Optional[DjangoProjectManager] = None
        self._uv: Optional[UvRunner] = None

    @property
    def djdevx_root(self) -> Path:
        """Lazily derive the djdevx root directory from file path."""
        if self._djdevx_root_cache is None:
            self._djdevx_root_cache = self._derive_djdevx_root(self._file_path)
        return self._djdevx_root_cache

    def _derive_djdevx_root(self, file_path: Path) -> Path:
        """Derive the djdevx root directory from file path.

        Handles both development setup and installed package scenarios:
        - Development: traverses up to find project root with djdevx/ and pyproject.toml
        - Installed: finds the djdevx package folder with templates/
        """
        current = file_path.parent
        while current != current.parent:  # until we hit filesystem root
            # Check development layout: project_root/djdevx/ and pyproject.toml
            if (current / "djdevx").exists() and (current / "pyproject.toml").exists():
                return current
            # Check installed layout: we're in djdevx package itself with templates/
            if current.name == "djdevx" and (current / "templates").exists():
                return current
            current = current.parent
        raise RuntimeError(f"Could not find djdevx root from {file_path}")

    @property
    def pm(self) -> DjangoProjectManager:
        """Lazy-loaded DjangoProjectManager."""
        if self._pm is None:
            self._pm = DjangoProjectManager()
        return self._pm

    @property
    def uv(self) -> UvRunner:
        """Lazy-loaded UvRunner."""
        if self._uv is None:
            self._uv = UvRunner()
        return self._uv

    def _uv_add_all(self) -> None:
        """Add all packages and dev_packages via uv."""
        for pkg in self.packages:
            self.uv.add_package(pkg)
        for pkg in self.dev_packages:
            self.uv.add_package(pkg, group="dev")

    def _strip_package_extras(self, pkg: str) -> str:
        """Strip extras from package name (e.g., 'package[extra]' -> 'package')."""
        return pkg.split("[")[0]

    def _remove_package_if_exists(self, pkg: str, group: str = "") -> None:
        """Remove package if it exists."""
        pkg_base = self._strip_package_extras(pkg)
        if self.pm.has_dependency(pkg_base, group):
            self.uv.remove_package(pkg_base, group=group)

    def _uv_remove_all(self) -> None:
        """Remove all packages and dev_packages."""
        for pkg in self.packages:
            self._remove_package_if_exists(pkg)
        for pkg in self.dev_packages:
            self._remove_package_if_exists(pkg, group="dev")

    def _copy_templates(self, context: dict[str, Any] = {}) -> None:
        """Copy templates to the project if they exist."""
        try:
            root = self.djdevx_root
            # Handle both development and installed scenarios
            if root.name == "djdevx":
                # Installed package: root is the djdevx package itself
                base_dir = root / "templates" / "django"
            else:
                # Development: root is project root, djdevx is a subfolder
                base_dir = root / "djdevx" / "templates" / "django"

            source_dir = base_dir / self._template_path

            if source_dir.exists():
                template_manager = TemplateManager()
                template_manager.copy_templates(
                    source_dir=source_dir,
                    dest_dir=self.pm.project_path,
                    template_context=context,
                )
        except RuntimeError:
            # djdevx root not found (should not happen with new logic)
            # Templates are optional, so silently skip
            pass

    def _cleanup_files(self) -> None:
        """Clean up auto-derived settings/URL files and ws_url_dirs."""
        settings_path = self.pm.packages_settings_path / self._settings_file
        settings_path.unlink(missing_ok=True)

        url_path = self.pm.packages_urls_path / self._url_file
        url_path.unlink(missing_ok=True)

        dir_path = self.pm.ws_urls_path / self._ws_url_dirs
        shutil.rmtree(dir_path, ignore_errors=True)

    def _sync_env_vars(self, operation: str = "add") -> None:
        """
        Sync environment variables with the project manager.

        Args:
            operation: Either "add" to add variables or "remove" to remove them.
        """
        if operation == "add":
            for key, value in self.env_vars.items():
                self.pm.add_env_variable(key, value)
        elif operation == "remove":
            for key in self.env_vars.keys():
                self.pm.remove_env_variable(key)

    def _add_env_vars(self) -> None:
        """Add all environment variables from env_vars dict."""
        self._sync_env_vars("add")

    def _remove_env_vars(self) -> None:
        """Remove all environment variables from env_vars dict."""
        self._sync_env_vars("remove")

    def install(self) -> None:
        """Install the package."""
        self._uv_add_all()
        self._copy_templates()
        self._add_env_vars()

    def remove(self) -> None:
        """Remove the package."""
        self._uv_remove_all()
        self._cleanup_files()
        self._remove_env_vars()

    def env(self) -> None:
        """Configure environment variables."""
        self._add_env_vars()

    @property
    def app(self) -> typer.Typer:
        """Build and return a Typer app with wrapped install/remove/env commands."""
        typer_app = typer.Typer(no_args_is_help=True)

        wrapped_install = self._wrap_command(
            self.install,
            f"Installing {self.name or 'package'}...",
            f"{self.name or 'Package'} installed successfully.",
        )
        typer_app.command(help=f"Install and configure {self.name or 'package'}")(
            wrapped_install
        )

        wrapped_remove = self._wrap_command(
            self.remove,
            f"Removing {self.name or ''} package...",
            f"{self.name or 'Package'} removed successfully.",
        )
        typer_app.command(help=f"Remove {self.name or ''} package")(wrapped_remove)

        has_custom_env = bool(self.env_vars) or type(self).env is not BasePackage.env
        if has_custom_env:
            wrapped_env = self._wrap_command(
                self.env,
                f"Configuring {self.name or 'package'} environment...",
                f"{self.name or 'Package'} environment configured successfully.",
            )
            typer_app.command()(wrapped_env)

        return typer_app

    def _wrap_command(
        self,
        method: Callable[..., Any],
        step_msg: str,
        success_msg: str,
    ) -> Callable[..., Any]:
        """
        Wrap a bound method with step/success prints using functools.wraps.

        This preserves the method's signature so Typer picks up typed parameters
        including Annotated[str, typer.Option(prompt=...)] correctly.
        """

        @functools.wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print_console.step(step_msg)
            result = method(*args, **kwargs)
            print_console.success(success_msg)
            return result

        return wrapper
