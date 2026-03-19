"""BasePackage class for standardized Django package installation management."""

import functools
import inspect
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Callable, Optional

import typer

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager
from ....utils.django.uv_runner import UvRunner
from ....utils.djdevx_config.backend.package_tracker import PackageTracker
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


@dataclass
class InstallParam:
    """Declares a parameter that contributes to template context during install."""

    name: str
    type_: type = str
    default: Any = ""
    help: str = ""
    prompt: Optional[str] = None
    show_if: Optional[str] = None
    message_before_prompt: Optional[str] = None
    hide_input: bool = False


class EnvType(str, Enum):
    """Classification of an environment variable for tracking purposes."""

    USER_INPUT = "user_input"  # plain value entered by the user
    SECRET = "secret"  # sensitive value (e.g. API key, password)
    RANDOM_SECRET = "random_secret"  # auto-generated random secret
    PRIVATE_SSH_KEY = "private_ssh_key"  # SSH private key


@dataclass
class EnvVar:
    """Declares an environment variable - either static or user-prompted.

    For static values: set ``env_key`` and ``value``.
    For prompted values: set ``env_key``, ``name``, and ``prompt``.

    Args:
        env_key: The environment variable key.
        value: Static value (leave empty for prompted vars).
        env_type: Classification of the variable (see ``EnvType``).
        name: CLI parameter name (required when ``prompt`` is set).
        type_: Python type for the CLI parameter.
        default: Default value for CLI parameter.
        help: Help text for CLI parameter.
        prompt: Prompt text shown to the user (if set, user will be prompted).
        hide_input: Whether to hide input (e.g. for secrets).
    """

    env_key: str
    value: str = ""
    env_type: EnvType = EnvType.USER_INPUT
    name: str = ""
    type_: type = str
    default: Any = ""
    help: str = ""
    prompt: Optional[str] = None
    hide_input: bool = False

    def __post_init__(self) -> None:
        """Auto-set hide_input for sensitive env types."""
        if self.env_type in (
            EnvType.SECRET,
            EnvType.RANDOM_SECRET,
            EnvType.PRIVATE_SSH_KEY,
        ):
            self.hide_input = True


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
    required_dependencies: list[str] = []
    env_vars: list["EnvVar"] = []
    settings_file: Optional[str] = None
    url_file: Optional[str] = None
    template_path: Optional[str] = None
    install_params: list[InstallParam] = []
    files_to_remove: list[str] = []
    folders_to_remove: list[str] = []

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

        self._pm: Optional[DjangoProjectManager] = None
        self._uv: Optional[UvRunner] = None
        self._install_context: dict[str, Any] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Auto-generate install/env methods for subclasses that declare params."""
        super().__init_subclass__(**kwargs)

        install_params: list[InstallParam] = cls.install_params
        # Prompted env vars drive CLI parameter generation
        prompted_env_vars = [
            env_var for env_var in cls.env_vars if env_var.prompt is not None
        ]

        has_params = bool(install_params) or bool(prompted_env_vars)
        install_overridden = "install" in cls.__dict__
        env_overridden = "env" in cls.__dict__

        if has_params and not install_overridden:
            # Capture for closure
            captured_install_params = list(install_params)
            captured_prompted_env_vars = list(prompted_env_vars)

            def generated_install(self, **kwargs: Any) -> None:  # type: ignore[override]
                """Install and configure the package."""
                self._install_context = {
                    install_param.name: kwargs[install_param.name]
                    for install_param in captured_install_params
                }

                self.before_uv_install()
                self._check_required_dependencies()
                self._uv_add_all()
                self.after_uv_install()
                self.before_copy_templates()

                for install_param in captured_install_params:
                    if install_param.show_if is not None:
                        gating_value = self._install_context[install_param.show_if]
                        if (
                            gating_value is True
                            and not self._install_context[install_param.name]
                        ):
                            if install_param.message_before_prompt:
                                typer.echo(install_param.message_before_prompt)
                            self._install_context[install_param.name] = typer.prompt(
                                install_param.prompt or install_param.name,
                                default=install_param.default,
                            )

                self._copy_templates(context=self._install_context)
                self.after_copy_templates()

                for env_var in captured_prompted_env_vars:
                    raw_value = kwargs[env_var.name]
                    value = str(raw_value) if isinstance(raw_value, Path) else raw_value
                    self.pm.add_env_variable(key=env_var.env_key, value=value)

                self._write_package_tracking()
                self._add_env_vars()

            cli_params = [
                inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            for install_param in captured_install_params:
                if install_param.show_if is None:
                    if install_param.prompt is not None:
                        annotation = Annotated[
                            install_param.type_,
                            typer.Option(
                                help=install_param.help,
                                prompt=install_param.prompt,
                                hide_input=install_param.hide_input,
                            ),
                        ]
                    else:
                        annotation = Annotated[
                            install_param.type_,
                            typer.Option(help=install_param.help),
                        ]
                else:
                    annotation = Annotated[
                        install_param.type_, typer.Option(help=install_param.help)
                    ]
                cli_params.append(
                    inspect.Parameter(
                        install_param.name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=install_param.default,
                        annotation=annotation,
                    )
                )
            for env_var in captured_prompted_env_vars:
                assert env_var.prompt is not None
                annotation = Annotated[
                    env_var.type_,
                    typer.Option(
                        help=env_var.help,
                        prompt=env_var.prompt,
                        hide_input=env_var.hide_input,
                    ),
                ]
                cli_params.append(
                    inspect.Parameter(
                        env_var.name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=env_var.default,
                        annotation=annotation,
                    )
                )

            generated_install.__signature__ = inspect.Signature(cli_params)  # type: ignore[attr-defined]
            generated_install.__name__ = "install"
            generated_install.__qualname__ = f"{cls.__name__}.install"
            cls.install = generated_install  # type: ignore[method-assign]

        if bool(prompted_env_vars) and not env_overridden:
            captured_prompted_env_vars_for_env = list(prompted_env_vars)

            def generated_env(self, **kwargs: Any) -> None:  # type: ignore[override]
                """Configure environment variables."""
                for env_var in captured_prompted_env_vars_for_env:
                    raw_value = kwargs[env_var.name]
                    value = str(raw_value) if isinstance(raw_value, Path) else raw_value
                    self.pm.add_env_variable(key=env_var.env_key, value=value)

            env_cli_params = [
                inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            for env_var in captured_prompted_env_vars_for_env:
                assert env_var.prompt is not None
                annotation = Annotated[
                    env_var.type_,
                    typer.Option(
                        help=env_var.help,
                        prompt=env_var.prompt,
                        hide_input=env_var.hide_input,
                    ),
                ]
                env_cli_params.append(
                    inspect.Parameter(
                        env_var.name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=env_var.default,
                        annotation=annotation,
                    )
                )

            generated_env.__signature__ = inspect.Signature(env_cli_params)  # type: ignore[attr-defined]
            generated_env.__name__ = "env"
            generated_env.__qualname__ = f"{cls.__name__}.env"
            cls.env = generated_env  # type: ignore[method-assign]

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
        """Clean up auto-derived settings and URL files."""
        settings_path = self.pm.packages_settings_path / self._settings_file
        settings_path.unlink(missing_ok=True)

        url_path = self.pm.packages_urls_path / self._url_file
        url_path.unlink(missing_ok=True)

    def _add_env_vars(self) -> None:
        """Add static environment variables from env_vars and write env tracking."""
        for env_var in self.env_vars:
            if (
                env_var.prompt is None
            ):  # static vars only; prompted vars come from user input
                self.pm.add_env_variable(env_var.env_key, env_var.value)
        self._write_env_tracking()

    def _remove_env_vars(self) -> None:
        """Remove all environment variables from env_vars and remove env tracking."""
        for env_var in self.env_vars:
            self.pm.remove_env_variable(env_var.env_key)
        try:
            PackageTracker().remove_env_entries(self._template_path)
        except (Exception, SystemExit):
            pass

    def _cleanup_extra_files(self) -> None:
        """Remove files and folders declared in files_to_remove / folders_to_remove."""
        for rel_path in self.files_to_remove:
            (self.pm.project_path / rel_path).unlink(missing_ok=True)
        for rel_path in self.folders_to_remove:
            shutil.rmtree(self.pm.project_path / rel_path, ignore_errors=True)

    def _check_required_dependencies(self) -> None:
        """
        Check if all required dependencies are installed.

        Raises:
            typer.Exit: If any required dependency is missing.
        """
        for dep in self.required_dependencies:
            if not self.pm.has_dependency(dep):
                print_console.error(
                    f"'{dep}' package is required for '{self.name}'. "
                    f"Please install that first."
                )
                print_console.info(f"\n> ddx backend django packages {dep} install")
                raise typer.Exit(code=1)

    def before_uv_install(self) -> None:
        """Hook called before uv install. Override in subclasses for pre-install logic."""
        ...

    def after_uv_install(self) -> None:
        """Hook called after uv install. Override in subclasses for post-install logic."""
        ...

    def before_copy_templates(self) -> None:
        """Hook called before templates are copied. Override in subclasses."""
        ...

    def after_copy_templates(self) -> None:
        """Hook called after templates are copied. Override in subclasses."""
        ...

    def before_uv_remove(self) -> None:
        """Hook called before uv remove. Override in subclasses for pre-remove logic."""
        ...

    def after_uv_remove(self) -> None:
        """Hook called after uv remove. Override in subclasses for post-remove logic."""
        ...

    def _write_package_tracking(self) -> None:
        """Write only the [package] section of config.toml under .djdevx/. Silently skipped if not a djdevx project."""
        try:
            PackageTracker().write_package_config(
                template_path=self._template_path,
                name=self.name,
            )
        except (Exception, SystemExit):
            pass

    def _write_env_tracking(self) -> None:
        """Write only the [env] section of config.toml under .djdevx/. Silently skipped if not a djdevx project."""
        try:
            env_entries: dict[str, str] = {}
            for env_var in self.env_vars:
                env_entries[env_var.env_key] = env_var.env_type.value
            if env_entries:
                PackageTracker().write_env_entries(
                    template_path=self._template_path,
                    env_entries=env_entries,
                )
        except (Exception, SystemExit):
            pass

    def _remove_tracking(self) -> None:
        """Delete the entire package tracking folder under .djdevx/. Silently skipped if not found."""
        try:
            PackageTracker().remove_package_config(self._template_path)
        except (Exception, SystemExit):
            pass

    def install(self) -> None:
        """Install the package."""
        self.before_uv_install()
        self._check_required_dependencies()
        self._uv_add_all()
        self.after_uv_install()
        self.before_copy_templates()
        self._copy_templates()
        self.after_copy_templates()
        self._write_package_tracking()
        self._add_env_vars()

    def remove(self) -> None:
        """Remove the package."""
        self.before_uv_remove()
        self._uv_remove_all()
        self.after_uv_remove()
        self._cleanup_files()
        self._cleanup_extra_files()
        self._remove_env_vars()
        self._remove_tracking()

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
            typer_app.command(
                help=f"Configure {self.name or 'package'} environment variables."
            )(wrapped_env)

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
            # Reset lazy-loaded project manager and uv runner so each command
            # invocation re-discovers the project path from the current working
            # directory. This is essential when the module-level _pkg instance is
            # shared across multiple test calls in the same process.
            self._pm = None
            self._uv = None
            print_console.step(step_msg)
            result = method(*args, **kwargs)
            print_console.success(success_msg)
            return result

        # If the underlying function has an injected __signature__ (from __init_subclass__),
        # functools.wraps copies it via __func__.__signature__, which includes `self`.
        # Fix by re-computing the signature from the bound method (which strips `self`).
        if hasattr(method, "__func__") and hasattr(method.__func__, "__signature__"):
            bound_sig = inspect.signature(method)
            wrapper.__signature__ = bound_sig  # type: ignore[attr-defined]

        return wrapper
