"""ProjectTracking — reads/writes djdevx.toml."""

from pathlib import Path
from typing import Optional

import tomlkit

from ..project.project_structure import ProjectStructure


class ProjectTracking:
    """Finds and manages djdevx.toml configuration."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        if project_root is not None:
            self._project_root = project_root
        else:
            self._project_root = ProjectStructure().root
        self._djdevx_path = self._project_root / "djdevx.toml"
        self._doc: Optional[tomlkit.TOMLDocument] = None

    @property
    def project_root(self) -> Path:
        return self._project_root

    def _load(self) -> tomlkit.TOMLDocument:
        if self._doc is None:
            if self._djdevx_path.exists():
                self._doc = tomlkit.loads(self._djdevx_path.read_text())
            else:
                self._doc = tomlkit.document()
        return self._doc

    def save(self) -> None:
        if self._doc is not None:
            self._djdevx_path.write_text(tomlkit.dumps(self._doc))

    def get_config(self) -> tomlkit.TOMLDocument:
        """Get the root config document."""
        return self._load()
