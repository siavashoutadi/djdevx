"""BasePackage class for standardized Django package installation management."""

from __future__ import annotations

import functools
import inspect
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Callable, Optional

import typer

from ....utils.console.print import print_console
from ....utils.django.project_manager import DjangoProjectManager
from ....utils.django.secret_manager import SecretManager
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
    """
    Declares a CLI parameter collected during install and passed to templates.

    When a subclass declares ``install_params``, BasePackage auto-generates a
    Typer ``install`` command whose options mirror these params. Values collected
    at install time are merged into the Jinja2 template context so settings and
    URL templates can be rendered with user-supplied configuration.

    Fields:
        name:                   Key in the template context dict and the CLI
                                ``--<name>`` option name.
        type_:                  Python type for the Typer option (default ``str``).
        default:                Default value when the option is not supplied.
        help:                   Help text shown next to the option in ``--help``.
        prompt:                 If set, Typer prompts the user interactively for
                                this value during install.
        show_if:                Name of another param in this list. When set, this
                                param is only prompted if the named param's value
                                is ``True`` and the current value is still empty.
                                Useful for optional sub-configuration (e.g. only
                                ask for a bucket name when S3 storage is enabled).
        message_before_prompt:  Text printed to stdout immediately before the
                                conditional prompt fires (``show_if`` path only).
        hide_input:             If ``True``, input is hidden in the terminal
                                (use for passwords and tokens).
    """

    name: str
    type_: type = str
    default: Any = ""
    help: str = ""
    prompt: Optional[str] = None
    show_if: Optional[str] = None
    message_before_prompt: Optional[str] = None
    hide_input: bool = False


class BasePackage:
    """
    Base class for Django packages with auto-registered install/remove commands.

    Subclasses declare class-level attributes to describe what to install, which
    templates to copy, and which secrets to generate. Override lifecycle hooks for
    custom logic — the base ``install()`` and ``remove()`` methods handle the
    standard flow automatically.

    Install lifecycle (in order):
        1. ``before_uv_install()``       — hook for pre-install checks/setup
        2. ``_check_required_dependencies()`` — exits if declared deps are missing
        3. ``_uv_add_all()``             — adds packages / dev_packages via uv
        4. ``after_uv_install()``        — hook for post-install uv steps
        5. ``before_copy_templates()``   — hook before template rendering
        6. ``_copy_templates()``         — renders and copies Jinja2 templates
        7. ``after_copy_templates()``    — hook after template rendering
        8. ``_write_package_tracking()`` — records install in .djdevx/config.toml
        9. ``_generate_secrets()``       — runs secret_generators, writes .secrets/

    Remove lifecycle (in order):
        1. ``before_uv_remove()``        — hook for pre-remove steps
        2. ``_uv_remove_all()``          — removes packages / dev_packages via uv
        3. ``after_uv_remove()``         — hook for post-remove steps
        4. ``_cleanup_files()``          — deletes auto-derived settings/URL files
        5. ``_cleanup_extra_files()``    — deletes files_to_remove / folders_to_remove
        6. ``_remove_tracking()``        — removes entry from .djdevx/config.toml

    Path auto-derivation from ``__file__``:
        Root packages  (packages/name.py)      → settings_file: name.py
                                                  url_file:      name.py
                                                  template_path: name
        Sub-packages   (packages/dir/name.py)  → settings_file: dir_name.py
                                                  url_file:      dir_name.py
                                                  template_path: dir/name

    Parameterised installs:
        Declare ``install_params`` to have BasePackage auto-generate a Typer
        ``install`` command with matching CLI options. Collected values are passed
        as Jinja2 context when copying templates.
    """

    # ------------------------------------------------------------------ #
    # Class-level configuration — override in subclasses as needed        #
    # ------------------------------------------------------------------ #

    # Human-readable display name used in CLI step/success messages.
    name: str = ""

    # PyPI package names added to the project via ``uv add`` during install.
    packages: list[str] = []

    # PyPI package names added to the dev dependency group via ``uv add --group dev``.
    dev_packages: list[str] = []

    # Other djdevx package names that must already be installed before this one.
    # Install exits with an error and a hint if any are missing.
    required_dependencies: list[str] = []

    # Override the auto-derived settings filename (default: see path auto-derivation).
    # Set only when the derived name would conflict with another package's file.
    settings_file: Optional[str] = None

    # Override the auto-derived URL filename (default: see path auto-derivation).
    url_file: Optional[str] = None

    # Override the auto-derived template directory path relative to
    # djdevx/templates/django/ (default: see path auto-derivation).
    template_path: Optional[str] = None

    # Declare CLI options collected at install time and passed to Jinja2 templates.
    # When non-empty and install() is not overridden, BasePackage auto-generates
    # a Typer install command whose --options mirror these params.
    install_params: list[InstallParam] = []

    # Project-relative file paths deleted by remove() in addition to the
    # auto-derived settings and URL files.
    files_to_remove: list[str] = []

    # Project-relative directory paths recursively deleted by remove().
    folders_to_remove: list[str] = []

    # Maps pydantic SecretStr field name → callable that returns the secret value.
    # Generators are called automatically at the end of install() and write their
    # output to .secrets/<field_name>. Skipped if the file already exists so
    # repeated installs are idempotent.
    # Field names must match the SecretStr fields declared in the package's
    # settings template — SettingCollector discovers them via AST parsing at runtime
    # so no parallel declaration is needed here.
    secret_generators: dict[str, Callable[[], str]] = {}

    # Auto-populated by __init_subclass__ — lists every subclass that has a
    # non-empty secret_generators dict. Used by SettingCollector to build the
    # generators index without manual registration.
    _generator_packages: list[type[BasePackage]] = []

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
        self._secret_manager: Optional[SecretManager] = None
        self._install_context: dict[str, Any] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Auto-generate install method for subclasses that declare install_params."""
        super().__init_subclass__(**kwargs)

        # Register in the auto-discovered generator packages list.
        if cls.secret_generators:
            cls._generator_packages.append(cls)

        install_params: list[InstallParam] = cls.install_params

        has_params = bool(install_params)
        install_overridden = "install" in cls.__dict__

        if has_params and not install_overridden:
            # Capture for closure
            captured_install_params = list(install_params)

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

                self._write_package_tracking()
                self._generate_secrets()

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

            generated_install.__signature__ = inspect.Signature(cli_params)  # type: ignore[attr-defined]
            generated_install.__name__ = "install"
            generated_install.__qualname__ = f"{cls.__name__}.install"
            cls.install = generated_install  # type: ignore[method-assign]

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

    @property
    def secret_manager(self) -> SecretManager:
        """Lazy-loaded SecretManager."""
        if self._secret_manager is None:
            self._secret_manager = SecretManager(self.pm.project_path)
        return self._secret_manager

    def _uv_add_all(self) -> None:
        """Add all packages and dev_packages via uv."""
        for pkg in self.packages:
            self.uv.add_package(pkg)
        for pkg in self.dev_packages:
            self.uv.add_package(pkg, group="dev")

    def _strip_package_extras(self, pkg: str) -> str:
        """Strip extras and version specifiers from package name."""
        name = pkg.split("[")[0]
        for sep in (">", "<", "=", "!", "~"):
            name = name.split(sep)[0]
        return name.strip()

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
        self._generate_secrets()

    def remove(self) -> None:
        """Remove the package."""
        self.before_uv_remove()
        self._uv_remove_all()
        self.after_uv_remove()
        self._cleanup_files()
        self._cleanup_extra_files()
        self._remove_tracking()

    def _generate_secrets(self) -> None:
        """
        Run secret_generators for this package and write results to .secrets/.

        Called automatically at the end of install(). Skips fields that already
        have a value in .secrets/ so repeated installs are idempotent.
        """
        for field_name, generator in self.secret_generators.items():
            if not self.secret_manager.has_secret(field_name):
                value = generator()
                self.secret_manager.write_secret(field_name, value)
                print_console.info(f"  Generated secret: {field_name}")

    @property
    def app(self) -> typer.Typer:
        """Build and return a Typer app with wrapped install and remove commands."""
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
