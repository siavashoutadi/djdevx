"""Create factory-boy factories for the models of the generated project."""

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
)
from . import mapper


def factory(models: list[str] | None = None) -> None:
    """Generate ``<app>/factories.py`` factories for the requested models.

    When *models* is None the user is prompted to pick models from the
    registered (non-Django) apps via a checkbox.
    """
    structure = ProjectStructure()
    commands = ManageCommands(PixiRunner(project_root=structure.root))
    available = introspect_models(commands)
    chosen = choose_models(
        models, available, prompt="Select the models to generate factories for"
    )
    generate_factories(chosen, available, structure)


def generate_factories(
    models: list[str],
    available: list[dict],
    structure: ProjectStructure,
) -> None:
    """Write factory-boy factories for already-resolved model labels.

    Shared by ``factory()`` and the ``seed-command`` generator so the seed
    management command can ensure factories exist before it references them.
    """
    by_app = group_models_by_app(models, available)
    written, added, skipped, updated = _write_factory_files(by_app, structure)
    format_files(written, structure.root)
    _print_summary(written, added, skipped, updated, structure)


def _write_factory_files(
    grouped: Mapping[str, list[dict]], structure: ProjectStructure
) -> tuple[list[Path], list[str], list[str], list[str]]:
    """Assemble and write ``factories.py`` for every app, one module per app.

    Returns ``(written, added, skipped, updated)`` where ``added`` lists the
    factory classes created, ``skipped`` those already complete and ``updated``
    existing classes that gained declarations from new model fields.
    """
    written: list[Path] = []
    added: list[str] = []
    skipped: list[str] = []
    updated: list[str] = []
    for app_label, model_infos in grouped.items():
        target = mapper.module_path(structure.root, app_label)
        existing = target.read_text() if target.exists() else None
        content, new_factories, already, refreshed = mapper.assemble_module(
            model_infos, existing=existing
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        written.append(target)
        added.extend(new_factories)
        skipped.extend(already)
        updated.extend(refreshed)
    return written, added, skipped, updated


def _print_summary(
    written: list[Path],
    added: list[str],
    skipped: list[str],
    updated: list[str],
    structure: ProjectStructure,
) -> None:
    """Summarize which modules were updated and factories added/skipped/refreshed."""
    for target in written:
        print_console.step_done(f"{target.relative_to(structure.root)} updated")
    for name in added:
        print_console.ok(f"Factory {name} added")
    for name in updated:
        print_console.ok(f"Factory {name} updated with new model fields")
    for name in skipped:
        print_console.info(f"Factory {name} already up to date, skipped")
