"""Create Django management commands that seed project models via factory-boy."""

from collections.abc import Mapping
from pathlib import Path

from djdevx.core.console import print_console
from djdevx.core.paths import ProjectStructure
from djdevx.core.process import PixiRunner
from djdevx.installable.ops.format import format_files
from djdevx.utils.django.manage_commands import ManageCommands
from djdevx.utils.django.models import (
    choose_models,
    group_models_by_app,
    introspect_models,
    models_by_label,
)
from ..factory_boy import generate_factories
from . import mapper


def seed_command(models: list[str] | None = None) -> None:
    """Generate ``<app>/management/commands/<app>.py`` seed commands.

    When *models* is None the user is prompted to pick models from the
    registered (non-Django) apps via a checkbox. Factory-boy factories are
    ensured for every chosen model (generated on the fly when missing) so the
    command can seed through them.
    """
    structure = ProjectStructure()
    commands = ManageCommands(PixiRunner(project_root=structure.root))
    available = introspect_models(commands)
    chosen = choose_models(
        models, available, prompt="Select the models to generate seed commands for"
    )
    generate_factories(chosen, available, structure)
    by_app = group_models_by_app(chosen, available)
    written, added, skipped = _write_command_files(by_app, available, structure)
    format_files(written, structure.root)
    _print_summary(written, added, skipped, structure)


def _write_command_files(
    grouped: Mapping[str, list[dict]],
    available: list[dict],
    structure: ProjectStructure,
) -> tuple[list[Path], list[str], list[str]]:
    """Assemble and write ``<app>/management/commands/<app>.py`` per app.

    Returns ``(written, added, skipped)`` where ``added`` lists the seed
    commands created and ``skipped`` those already present in the target file.
    """
    by_label = models_by_label(available)
    written: list[Path] = []
    added: list[str] = []
    skipped: list[str] = []
    for app_label, model_infos in grouped.items():
        target = mapper.module_path(structure.root, app_label)
        existing = target.read_text() if target.exists() else None
        existing_names = (
            mapper.existing_model_names(existing) if existing is not None else []
        )
        chosen_names = [f"{app_label}.{m['name']}" for m in model_infos]

        new_models = [m for m in model_infos if m["name"] not in existing_names]
        if not new_models:
            skipped.extend(chosen_names)
            continue

        union_names = [
            name for name in existing_names if f"{app_label}.{name}" in by_label
        ]
        union_names.extend(m["name"] for m in new_models)

        content = mapper.build_module(
            app_label, [by_label[f"{app_label}.{n}"] for n in union_names]
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        written.append(target)
        added.extend(chosen_names)
    return written, added, skipped


def _print_summary(
    written: list[Path],
    added: list[str],
    skipped: list[str],
    structure: ProjectStructure,
) -> None:
    """Summarize which seed commands were added/skipped."""
    for target in written:
        print_console.step_done(f"{target.relative_to(structure.root)} updated")
    for name in added:
        print_console.ok(f"Seed command for {name} added")
    for name in skipped:
        print_console.info(f"Seed command for {name} already present, skipped")
