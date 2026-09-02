"""ProjectTracking — reads/writes djdevx.toml and manages section entries."""

from pathlib import Path
from typing import Any, Optional

import tomlkit

from ..project.project_structure import ProjectStructure
from .sections import Section

Table = dict[str, Any]

_APPLIED_PEERS_KEY = "peer_pixi_applied"


class ProjectTracking:
    """The project tracking facade.

    Owns the djdevx.toml document (load/save) and provides section-scoped
    operations on ``[<section>.<name>]`` entries. Reads never mutate the
    document; mutations trigger a save.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        if project_root is not None:
            self._project_root = project_root
        else:
            self._project_root = ProjectStructure().root
        self._djdevx_path = self._project_root / "djdevx.toml"
        self._doc: Optional[tomlkit.TOMLDocument] = None

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

    def _get_table(self, section: Section) -> Optional[Table]:
        """Return the section table, or None if the section is absent."""
        config = self._load()
        table = config.get(section)
        return table if table is not None else None

    def _ensure_table(self, section: Section) -> Table:
        """Return the section table, creating it if absent."""
        config = self._load()
        table = config.get(section)
        if table is None:
            table = tomlkit.table()
            config[section] = table
        return table

    # ------------------------------------------------------------------
    # Section-scoped operations
    # ------------------------------------------------------------------

    def add(
        self,
        section: Section,
        name: str,
        display_name: Optional[str] = None,
        *,
        variant: Optional[str] = None,
        variants: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        table = self._ensure_table(section)
        if name not in table:
            table[name] = tomlkit.table()
        entry = table[name]
        entry["installed"] = True
        if display_name is not None:
            entry["display_name"] = display_name
        if variant is not None:
            entry["variant"] = variant
        if variants is not None:
            entry["variants"] = variants
        if metadata:
            for key, value in metadata.items():
                entry[key] = value
        self.save()

    def remove(self, section: Section, name: str) -> None:
        table = self._get_table(section)
        if table is not None and name in table:
            del table[name]
            self.save()

    def is_installed(self, section: Section, name: str) -> bool:
        table = self._get_table(section)
        return table is not None and name in table

    def get_variants(self, section: Section, name: str) -> list[str]:
        table = self._get_table(section)
        if table is not None:
            entry = table.get(name)
            if entry is not None and hasattr(entry, "get"):
                v = entry.get("variants")
                return list(v) if v else []
        return []

    def get_metadata(self, section: Section, name: str, key: str, default=None) -> Any:
        table = self._get_table(section)
        if table is not None:
            entry = table.get(name)
            if entry is not None and hasattr(entry, "get"):
                return entry.get(key, default)
        return default

    def set_metadata(self, section: Section, name: str, key: str, value: Any) -> None:
        table = self._ensure_table(section)
        if name not in table:
            table[name] = tomlkit.table()
        entry = table[name]
        entry[key] = value
        self.save()

    def get_applied_peers(self, section: Section, name: str) -> set[str]:
        """Return the set of applied peer packages for *name* in *section*."""
        value = self.get_metadata(section, name, _APPLIED_PEERS_KEY, [])
        return set(value) if value else set()

    def set_applied_peers(self, section: Section, name: str, keys: set[str]) -> None:
        """Persist the set of applied peer packages for *name* in *section*."""
        self.set_metadata(section, name, _APPLIED_PEERS_KEY, list(keys))

    def list(self, section: Section) -> dict[str, dict[str, Any]]:
        table = self._get_table(section)
        result: dict[str, dict[str, Any]] = {}
        if table is None:
            return result
        for k, v in table.items():
            info: dict[str, Any] = {}
            if "display_name" in v:
                info["display_name"] = v["display_name"]
            if "variant" in v:
                info["variant"] = v["variant"]
            if "variants" in v:
                info["variants"] = list(v["variants"])

            if info:
                result[k] = info
            else:
                result[k] = {}
        return result

    def installed(self, section: Section) -> Optional[str]:
        """Return the single installed name in the section, or None."""
        return next(iter(self.list(section)), None)
