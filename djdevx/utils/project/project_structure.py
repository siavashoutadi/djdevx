"""ProjectStructure — single source of truth for all project paths."""

from pathlib import Path
from typing import Optional


class ProjectStructure:
    """Resolves all project directory paths relative to the root.

    Finds the project root by walking up from CWD looking for ``djdevx.toml``,
    or accepts an explicit *root* for testing.
    """

    def __init__(self, root: Optional[Path] = None):
        self._root = root or self._find_root()

    @staticmethod
    def _find_root() -> Path:
        """Walk up from CWD to find djdevx.toml."""
        current = Path.cwd()
        while current != current.parent:
            if (current / "djdevx.toml").exists():
                return current
            current = current.parent
        raise RuntimeError(
            "Could not find a djdevx.toml. Are you in a project managed by djdevx?"
        )

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    @property
    def root(self) -> Path:
        return self._root

    @property
    def djdevx_toml(self) -> Path:
        return self._root / "djdevx.toml"

    @property
    def gitignore_path(self) -> Path:
        return self._root / ".gitignore"

    @property
    def dockerfile_path(self) -> Path:
        return self._root / "Dockerfile"

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    @property
    def settings_dir(self) -> Path:
        return self._root / "settings"

    @property
    def django_settings_dir(self) -> Path:
        return self._root / "settings" / "django"

    @property
    def packages_settings_dir(self) -> Path:
        return self._root / "settings" / "packages"

    # ------------------------------------------------------------------
    # URLs
    # ------------------------------------------------------------------

    @property
    def urls_dir(self) -> Path:
        return self._root / "urls"

    @property
    def packages_urls_dir(self) -> Path:
        return self._root / "urls" / "packages"

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------

    @property
    def templates_dir(self) -> Path:
        return self._root / "templates"

    @property
    def base_template(self) -> Path:
        return self._root / "templates" / "_base.html"

    # ------------------------------------------------------------------
    # Static
    # ------------------------------------------------------------------

    @property
    def static_dir(self) -> Path:
        return self._root / "static"

    @property
    def static_css_dir(self) -> Path:
        return self._root / "static" / "css"

    @property
    def static_js_dir(self) -> Path:
        return self._root / "static" / "js"

    # ------------------------------------------------------------------
    # Devcontainer
    # ------------------------------------------------------------------

    @property
    def devcontainer_dir(self) -> Path:
        return self._root / ".devcontainer"

    # ------------------------------------------------------------------
    # Tailwind
    # ------------------------------------------------------------------

    @property
    def tailwind_input_css(self) -> Path:
        return self._root / "tailwind" / "src" / "css" / "input.css"

    # ------------------------------------------------------------------
    # Local dev data
    # ------------------------------------------------------------------

    @property
    def dev_data_dir(self) -> Path:
        return self._root / ".pixi" / "devdata"
