"""Create factory-boy factories for the models of the generated project."""

from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path

import typer

from djdevx.core.console import print_console
from djdevx.core.paths import ProjectStructure
from djdevx.core.process import PixiRunner
from djdevx.installable.ops.format import format_files
from djdevx.utils.django.manage_commands import ManageCommands
from ...utils.console import prompts
from . import introspect, mapper


def factory(models: list[str] | None = None) -> None:
    """Generate ``<app>/factories.py`` factories for the requested models.

    When *models* is None the user is prompted to pick models from the
    registered (non-Django) apps via a checkbox.
    """
    structure = ProjectStructure()
    commands = ManageCommands(PixiRunner(project_root=structure.root))
    available = _introspect_models(commands)
    chosen = _choose_models_for_factories(models, available)
    by_app = _group_models_by_app(chosen, available)
    written, added, skipped, updated = _write_factory_files(by_app, structure)
    format_files(written, structure.root)
    _print_summary(written, added, skipped, updated, structure)


def _introspect_models(commands: ManageCommands) -> list[dict]:
    """Introspect the project's models, failing with a friendly error."""
    try:
        return introspect.list_models(commands)
    except introspect.IntrospectionError as exc:
        print_console.error(str(exc))
        raise typer.Exit(code=1)


def _choose_models_for_factories(
    models: list[str] | None, available: list[dict]
) -> list[str]:
    """Resolve the wanted model labels from CLI args or the checkbox prompt."""
    labels = [f"{model['app_label']}.{model['name']}" for model in available]
    if models:
        wanted = models
    else:
        selected = prompts.checkbox(
            "Select the models to generate factories for", choices=labels
        )
        if not selected:
            raise typer.Abort()
        wanted = selected

    by_label = {f"{m['app_label']}.{m['name']}": m for m in available}
    missing = [label for label in wanted if label not in by_label]
    if missing:
        print_console.error(f"Unknown model(s): {', '.join(missing)}")
        raise typer.Exit(code=1)
    return wanted


def _group_models_by_app(
    chosen: list[str], available: list[dict]
) -> dict[str, list[dict]]:
    """Group the chosen models by their app label."""
    by_label = {f"{model['app_label']}.{model['name']}": model for model in available}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for label in chosen:
        model = by_label[label]
        grouped[model["app_label"]].append(model)
    return grouped


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
