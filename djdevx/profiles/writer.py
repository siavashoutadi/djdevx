"""Interactive profile creation and generation from an existing project."""

from pathlib import Path
from typing import Any

import typer

from ..utils.console import prompts
from ..utils.tracking import ProjectTracking

from .installer import _ensure_registries, _registry_for, available_names
from .models import Profile, ProfileInstallable

_SECTION_LABELS = {
    "packages": "package",
    "features": "feature",
    "frameworks": "framework",
    "database": "database",
    "cache": "cache",
}


def _abort_on_cancel(answer: Any) -> Any:
    """Abort the profile creation when the user cancels a prompt (Ctrl+C).

    questionary swallows ``KeyboardInterrupt`` and returns ``None``, which is
    indistinguishable from a plain cancel.  An empty checkbox selection returns
    ``[]`` and is handled by the caller, not here.
    """
    if answer is None:
        raise typer.Abort()
    return answer


def create_profile_interactive() -> tuple[Profile, dict[str, dict]]:
    """Interactively build a Profile and answers dict.

    Returns ``(profile, answers)`` where answers maps section → name → params.
    """
    _ensure_registries()

    profile = Profile()
    answers: dict[str, dict] = {}

    sections = [
        ("packages", "packages to install"),
        ("features", "features to install"),
        ("frameworks", "frameworks to install"),
        ("database", "database to install"),
        ("cache", "cache to install"),
    ]

    for section_key, label in sections:
        registry = _registry_for(section_key)
        names = available_names(section_key)
        if not names:
            continue

        choices = [
            prompts.Choice(title=_display_name(registry, n), value=n) for n in names
        ]
        selected = _abort_on_cancel(
            prompts.checkbox(f"Select {label}:", choices=choices)
        )
        if not selected:
            continue

        section_profile = {}
        section_answers = {}

        for name in selected:
            cls = registry.get(name)
            installable = cls()
            entry = ProfileInstallable()
            entry_answers = {}

            if installable.variants:
                if installable.exclusive_variants:
                    variant_names = list(installable.variants.keys())
                    variant_choices = [
                        prompts.Choice(
                            title=installable.variants[v].display_name, value=v
                        )
                        for v in variant_names
                    ]
                    chosen = _abort_on_cancel(
                        prompts.select(
                            f"Which provider for {_display_name(registry, name)}?",
                            choices=variant_choices,
                        )
                    )
                    if chosen:
                        entry.variant = chosen
                        answers_for_variant = {}
                        _collect_param_answers(
                            installable.variants[chosen],
                            f"{name} ({chosen})",
                            answers_for_variant,
                        )
                        if answers_for_variant:
                            entry_answers[chosen] = answers_for_variant
                else:
                    required = [
                        v for v, var in installable.variants.items() if var.required
                    ]
                    optional = [
                        prompts.Choice(
                            title=installable.variants[v].display_name, value=v
                        )
                        for v, var in installable.variants.items()
                        if not var.required
                    ]
                    chosen_variants = list(required)
                    if optional:
                        extra = _abort_on_cancel(
                            prompts.checkbox(
                                f"Which additional functionalities for "
                                f"{_display_name(registry, name)}?",
                                choices=optional,
                            )
                        )
                    if extra:
                        chosen_variants.extend(extra)
                    if chosen_variants:
                        entry.variants = chosen_variants
                    for v in chosen_variants:
                        answers_for_variant = {}
                        _collect_param_answers(
                            installable.variants[v],
                            f"{name} ({v})",
                            answers_for_variant,
                        )
                        if answers_for_variant:
                            entry_answers[v] = answers_for_variant
            else:
                _collect_param_answers(
                    installable, _display_name(registry, name), entry_answers
                )

            section_profile[name] = entry
            if entry_answers:
                section_answers[name] = entry_answers

        setattr(profile, section_key, section_profile)
        if section_answers:
            answers[section_key] = section_answers

    return profile, answers


def _display_name(registry, name: str) -> str:
    """Display name for an installable, falling back to its key name."""
    cls = registry.get(name)
    value = cls.model_fields.get("display_name")
    if value is not None and value.default:
        return value.default
    return name


def _collect_param_answers(
    installable_or_variant,
    label: str,
    answers: dict,
) -> None:
    """Prompt for install params and store values in ``answers``."""
    for param in installable_or_variant.install_params:
        if param.prompt is None:
            continue
        default = str(param.default) if param.default else ""
        if param.hide_input:
            value = _abort_on_cancel(
                prompts.password(f"{label}: {param.prompt}", default=default)
            )
        elif param.type_ is bool:
            value = _abort_on_cancel(
                prompts.confirm(f"{label}: {param.prompt}", default=bool(param.default))
            )
        else:
            value = _abort_on_cancel(
                prompts.text(f"{label}: {param.prompt}", default=default)
            )
        answers[param.name] = value


def generate_profile_from_project(project_root: Path | None = None) -> Profile:
    """Build a Profile from an existing project's djdevx.toml tracking state."""
    tracking = ProjectTracking(project_root)
    config = tracking.get_config()

    profile = Profile()

    for section_key in ("packages", "features", "frameworks", "database", "cache"):
        section_data = config.get(section_key)
        if not isinstance(section_data, dict):
            continue
        section_profile = {}
        for name in section_data:
            entry_config = section_data[name]
            entry = ProfileInstallable()
            if isinstance(entry_config, dict):
                variant = entry_config.get("variant")
                if variant:
                    entry.variant = variant
                variants = entry_config.get("variants")
                if variants:
                    entry.variants = list(variants)
            section_profile[name] = entry
        setattr(profile, section_key, section_profile)

    return profile


def write_profile_toml(profile: Profile, path: Path) -> None:
    """Serialize a Profile to TOML."""
    from tomlkit import inline_table, table

    doc = table()

    if profile.new.python_version or profile.new.project_description:
        new_table = table()
        if profile.new.project_description:
            new_table["project_description"] = profile.new.project_description
        if profile.new.python_version:
            new_table["python_version"] = profile.new.python_version
        doc["new"] = new_table

    for section_key in (
        "packages",
        "features",
        "frameworks",
        "database",
        "cache",
    ):
        entries = getattr(profile, section_key)
        if not entries:
            continue
        section_table = table()
        for name, entry in entries.items():
            entry_table = inline_table()
            if entry.variant:
                entry_table["variant"] = entry.variant
            if entry.variants:
                entry_table["variants"] = list(entry.variants)
            section_table[name] = entry_table
        doc[section_key] = section_table

    path.write_text(_toml_dumps(doc))


def write_answers_toml(answers: dict[str, dict], path: Path) -> None:
    """Serialize answers (section → name → params) to TOML."""
    from tomlkit import table

    doc = table()

    for section_key, names in answers.items():
        section_table = table()
        for name, params in names.items():
            entry_table = table()
            for key, value in params.items():
                entry_table[key] = value
            section_table[name] = entry_table
        doc[section_key] = section_table

    path.write_text(_toml_dumps(doc))


def _toml_dumps(doc) -> str:
    from tomlkit import dumps

    return dumps(doc)
