"""Shared model discovery and resolution helpers for model-based generators.

Both the factory-boy generator and the seed-command generator introspect the
project's models, pick a subset via CLI args or a checkbox prompt, and group
the chosen models by app label. These helpers centralize that logic so the two
generators stay in sync.
"""

from collections import defaultdict

import typer

from djdevx.core.console import print_console
from djdevx.utils.console import prompts
from djdevx.utils.django import introspect
from djdevx.utils.django.manage_commands import ManageCommands


def model_label(model: dict) -> str:
    """Return the ``app_label.ModelName`` label for an introspected model."""
    return f"{model['app_label']}.{model['name']}"


def models_by_label(available: list[dict]) -> dict[str, dict]:
    """Index introspected models by their ``app_label.ModelName`` label."""
    return {model_label(model): model for model in available}


def introspect_models(commands: ManageCommands) -> list[dict]:
    """Introspect the project's models, failing with a friendly error."""
    try:
        return introspect.list_models(commands)
    except introspect.IntrospectionError as exc:
        print_console.error(str(exc))
        raise typer.Exit(code=1)


def choose_models(
    models: list[str] | None, available: list[dict], *, prompt: str
) -> list[str]:
    """Resolve the wanted model labels from CLI args or a checkbox prompt."""
    labels = [model_label(model) for model in available]
    if models:
        wanted = models
    else:
        selected = prompts.checkbox(prompt, choices=labels)
        if not selected:
            raise typer.Abort()
        wanted = selected

    by_label = models_by_label(available)
    missing = [label for label in wanted if label not in by_label]
    if missing:
        print_console.error(f"Unknown model(s): {', '.join(missing)}")
        raise typer.Exit(code=1)
    return wanted


def group_models_by_app(
    chosen: list[str], available: list[dict]
) -> dict[str, list[dict]]:
    """Group the chosen models by their app label."""
    by_label = models_by_label(available)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for label in chosen:
        model = by_label[label]
        grouped[model["app_label"]].append(model)
    return grouped
