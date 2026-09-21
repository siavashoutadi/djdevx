"""Create a timestamped abstract base model in a Django app."""

import re
from pathlib import Path

import typer

from djdevx.core.console import print_console
from djdevx.core.paths import ProjectStructure
from ...utils.templates.manager import TemplateManager

_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def validate_app_name(value: str) -> str:
    """Validate that the value is a valid Django application name."""
    if not _IDENTIFIER_RE.fullmatch(value):
        raise typer.BadParameter(f"'{value}' is not a valid Django application name.")
    return value


def validate_class_name(value: str) -> str:
    """Validate that the value is a valid Python class name."""
    if not _IDENTIFIER_RE.fullmatch(value):
        raise typer.BadParameter(f"'{value}' is not a valid Python class name.")
    return value


def _app_config_class(app_name: str) -> str:
    """Camelize an app name into its AppConfig class name (core -> CoreConfig)."""
    return "".join(part.capitalize() for part in re.split(r"[_-]+", app_name))


def base_model(app_name: str = "core", class_name: str = "TimeStampedModel") -> None:
    """Create a timestamped abstract base model in a Django app."""
    structure = ProjectStructure()
    current_dir = Path(__file__).resolve().parent

    print_console.step(f"Creating base model {class_name!r} in app {app_name!r}")
    TemplateManager().copy_templates(
        source_dir=current_dir / "templates",
        dest_dir=structure.root,
        template_context={
            "app_name": app_name,
            "class_name": class_name,
            "app_config_class": f"{_app_config_class(app_name)}Config",
        },
    )
    print_console.step_done(f"Base model {class_name!r} created in app {app_name!r}")
