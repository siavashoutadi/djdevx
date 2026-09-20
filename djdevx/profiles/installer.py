"""Batch-install logic — installs everything defined in a profile."""

from typing import Any

from djdevx.core.console import print_console
from ..core.discovery import discover_and_register
from ..installable.orchestrator import add_installable
from ..installable.models import (
    CACHE,
    DATABASE,
    FEATURE,
    FRAMEWORK,
    PACKAGE,
    InstallableConfig,
    InstallableKind,
)
from ..installable.registry import REGISTRIES

from .models import AnswersFile, Profile, ProfileInstallable

_KIND_BY_SECTION: dict[str, InstallableKind] = {
    "packages": PACKAGE,
    "features": FEATURE,
    "frameworks": FRAMEWORK,
    "database": DATABASE,
    "cache": CACHE,
}

_SECTION_BASES = {}


def _ensure_registries() -> None:
    """Import every provider module so all installables are registered."""
    from ..providers import cache as _cache
    from ..providers import database as _db
    from ..providers import features as _feat
    from ..providers import frameworks as _fw
    from ..providers import packages as _pkg

    discover_and_register(_pkg.__path__, "djdevx.providers.packages")
    discover_and_register(_feat.__path__, "djdevx.providers.features")
    discover_and_register(_fw.__path__, "djdevx.providers.frameworks")
    discover_and_register(_db.__path__, "djdevx.providers.database")
    discover_and_register(_cache.__path__, "djdevx.providers.cache")


def _registry_for(section_key: str):
    _ensure_registries()
    return REGISTRIES[_KIND_BY_SECTION[section_key].name]


def _resolve_answers_for(
    answers: AnswersFile | None,
    section_key: str,
    name: str,
    variants: list[str],
) -> dict[str, Any]:
    """Merge answer values for an installable and its selected variants."""
    if answers is None:
        return {}

    section_data = getattr(answers, section_key, {})
    entry = section_data.get(name)
    if not isinstance(entry, dict):
        return {}

    merged: dict[str, Any] = {}
    for variant in variants:
        variant_data = entry.get(variant)
        if isinstance(variant_data, dict):
            if "params" in variant_data:
                merged.update(variant_data["params"])
            else:
                merged.update(variant_data)

    params = entry.get("params")
    if isinstance(params, dict):
        merged.update(params)

    if not variants:
        top_level = {
            k: v for k, v in entry.items() if k != "params" and not isinstance(v, dict)
        }
        merged.update(top_level)

    return merged


def install_profile(
    profile: Profile,
    answers: AnswersFile | None = None,
    verbose: bool = False,
) -> None:
    """Install all items defined in a profile.

    Iterates each installable domain (packages, features, frameworks,
    database, cache), resolves the installable class, collects its answers,
    and installs it via the shared orchestrator.
    """
    _ensure_registries()

    any_installed = False
    sections = [
        ("packages", profile.packages),
        ("features", profile.features),
        ("frameworks", profile.frameworks),
        ("database", profile.database),
        ("cache", profile.cache),
    ]
    for section_key, section_items in sections:
        for name, entry in section_items.items():
            installed = _install_entry(name, entry, section_key, answers, verbose)
            any_installed = any_installed or installed

    if not any_installed:
        print_console.info("No installables in profile — nothing to install.")


def _install_entry(
    name: str,
    entry: ProfileInstallable,
    section_key: str,
    answers: AnswersFile | None,
    verbose: bool,
) -> bool:
    """Install a single profile entry. Returns True on success."""
    normalized = InstallableConfig.normalize_name(name)

    try:
        cls = _registry_for(section_key).get(normalized)
    except KeyError:
        print_console.warning(f"Unknown {section_key[:-1]} '{name}'. Skipping.")
        return False

    variants = list(entry.variants or [])
    if entry.variant and entry.variant not in variants:
        variants.insert(0, entry.variant)

    resolved_answers = _resolve_answers_for(answers, section_key, name, variants)

    try:
        return add_installable(
            cls,
            normalized,
            provider=entry.variant,
            verbose=verbose,
            is_multi=True,
            answers=resolved_answers,
            variants=variants if entry.variant is None else None,
        )
    except SystemExit, KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 — surface per-package failures inline
        print_console.fail(f"Failed to install {name}: {exc}")
        return False


def available_names(section_key: str) -> list[str]:
    """Return all registered installable names for a section."""
    return _registry_for(section_key).names()
