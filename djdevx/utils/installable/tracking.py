"""Installable tracking queries — standalone functions taking cls (like list_table.py)."""

from pathlib import Path
from typing import Optional

from ..tracking import ProjectTracking, Section


def _normalize(name: str) -> str:
    return name.replace("_", "-")


class TrackingOps:
    """Section-scoped tracking operations for installable lifecycle."""

    def __init__(self, section: Section, project_root: Optional[Path] = None):
        self._section = section
        self._project = ProjectTracking(project_root)

    def track_install(self, instance, variant=None) -> None:
        name = _normalize(instance.name)
        if variant:
            existing = self._project.get_variants(self._section, name)
            variant_name = variant.name
            if variant_name and variant_name not in existing:
                existing = existing + [variant_name]
            self._project.add(
                self._section, name, instance.display_name, variants=existing
            )
        else:
            self._project.add(self._section, name, instance.display_name)

    def get_variants(self, name: str) -> list[str]:
        return self._project.get_variants(self._section, _normalize(name))

    def remove(self, name: str) -> None:
        self._project.remove(self._section, _normalize(name))

    def add(self, name: str, display_name: str, variants=None) -> None:
        self._project.add(
            self._section, _normalize(name), display_name, variants=variants
        )


def get_section(cls) -> Section:
    field = cls.model_fields.get("section")
    if field is None:
        raise ValueError(f"{cls.__name__} does not declare a 'section' field")
    value = field.default
    if value is None:
        value = field.default_factory() if field.default_factory else Section.PACKAGES
    return value


def get_installed_names(cls) -> dict:
    return ProjectTracking().list(get_section(cls))


def get_available_names(cls) -> list[str]:
    return cls.get_registry().list()


def get_installed_variants(cls, name: str) -> list[str]:
    return ProjectTracking().get_variants(get_section(cls), name)


def get_installable_names(cls) -> list[str]:
    installed = set(get_installed_names(cls))
    return [n for n in get_available_names(cls) if n not in installed]


def get_display_name(cls, name: str) -> str:
    try:
        installable_cls = cls.get_registry().get(name)
        return installable_cls.model_fields["display_name"].default or name
    except KeyError:
        return name


def autocomplete_installable(cls, incomplete: str) -> list[str]:
    return [
        n
        for n in get_installable_names(cls)
        if not incomplete or n.startswith(incomplete)
    ]


def autocomplete_installed(cls, incomplete: str) -> list[str]:
    return [
        n
        for n in get_installed_names(cls)
        if not incomplete or n.startswith(incomplete)
    ]


def track_install(instance, variant=None) -> None:
    """Record the install in djdevx.toml."""
    TrackingOps(get_section(type(instance))).track_install(instance, variant)
