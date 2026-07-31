"""SectionTracking — manages a named section in djdevx.toml."""

from pathlib import Path
from typing import Optional

import tomlkit

from .project import ProjectTracking


class SectionTracking:
    """Read/write [<section>.<name>] entries in djdevx.toml."""

    def __init__(self, section: str, project_root: Optional[Path] = None) -> None:
        self._section = section
        self._project = ProjectTracking(project_root)

    def _get_table(self) -> tomlkit.TOMLDocument:
        config = self._project.get_config()
        if self._section not in config:
            config[self._section] = tomlkit.table()
        return config[self._section]

    def add(
        self,
        name: str,
        display_name: Optional[str] = None,
        *,
        variant: Optional[str] = None,
        variants: Optional[list[str]] = None,
    ) -> None:
        table = self._get_table()
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
        self._project.save()

    def remove(self, name: str) -> None:
        table = self._get_table()
        if name in table:
            del table[name]
            self._project.save()

    def is_installed(self, name: str) -> bool:
        table = self._get_table()
        return name in table

    def get_variants(self, name: str) -> list[str]:
        table = self._get_table()
        entry = table.get(name)
        if entry is not None and hasattr(entry, "get"):
            v = entry.get("variants")
            return list(v) if v else []
        return []

    def list(self) -> dict:
        table = self._get_table()
        result = {}
        for k, v in table.items():
            info = {}
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
