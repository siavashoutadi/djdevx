"""Build Django management command modules that seed models via factory-boy."""

from pathlib import Path

_HEADER = """\
import typer

from typing import Annotated
from django_typer.management import TyperCommand, command"""


def _plural(model_name: str) -> str:
    """Lowercase + ``s`` plural used for help/echo text (matches users.py style)."""
    return f"{model_name.lower()}s"


def _seed_method(model: dict) -> str:
    name = model["name"]
    plural = _plural(name)
    return (
        "    @command()\n"
        f"    def seed_{name.lower()}(\n"
        "        self,\n"
        f'        count: Annotated[int, typer.Option(help="Number of {plural} to create")] = 5,\n'
        "    ):\n"
        f'        """Create {plural} via factory-boy."""\n'
        f'        typer.echo(f"Creating {{count}} {plural} ...")\n'
        f"        {name}Factory.create_batch(count)\n"
        f'        typer.echo(f"{{count}} {plural} created.")'
    )


def _clean_method(model: dict) -> str:
    name = model["name"]
    plural = _plural(name)
    return (
        "    @command()\n"
        f"    def clean_{name.lower()}(self):\n"
        f'        """Delete all {plural}."""\n'
        f'        typer.echo("Deleting all {plural} ...")\n'
        f"        {name}.objects.all().delete()\n"
        f'        typer.echo("All {plural} deleted.")'
    )


def _seed_all_method(model_infos: list[dict]) -> str:
    """Build the ``seed_all`` subcommand that runs every per-model seed."""
    calls = "\n".join(
        f"        self.seed_{m['name'].lower()}(count=count)" for m in model_infos
    )
    return (
        "    @command()\n"
        "    def seed_all(\n"
        "        self,\n"
        '        count: Annotated[int, typer.Option(help="Number of each model to create")] = 5,\n'
        "    ):\n"
        '        """Seed all app models via factory-boy."""\n'
        '        typer.echo("Seeding all models ...")\n'
        f"{calls}\n"
        '        typer.echo("All models seeded.")'
    )


def _clean_all_method(model_infos: list[dict]) -> str:
    """Build the ``clean_all`` subcommand that runs every per-model clean."""
    calls = "\n".join(f"        self.clean_{m['name'].lower()}()" for m in model_infos)
    return (
        "    @command()\n"
        "    def clean_all(self):\n"
        '        """Delete all app models."""\n'
        '        typer.echo("Deleting all models ...")\n'
        f"{calls}\n"
        '        typer.echo("All models deleted.")'
    )


def build_module(app_label: str, model_infos: list[dict]) -> str:
    """Build the source of an app's seed management command module."""
    names = [model["name"] for model in model_infos]
    imports = (
        f"from {app_label}.factories import "
        f"{', '.join(f'{name}Factory' for name in names)}\n"
        f"from {app_label}.models import {', '.join(names)}"
    )
    methods = [_seed_all_method(model_infos)]
    for model in model_infos:
        methods.append(_seed_method(model))
        methods.append(_clean_method(model))
    methods.append(_clean_all_method(model_infos))
    body = "\n\n".join(methods)
    return (
        f"{_HEADER}\n\n{imports}\n\n\n"
        f"class Command(TyperCommand):\n"
        f'    """Seed and clean the {app_label} app models."""\n'
        f"\n{body}\n"
    )


def existing_model_names(source: str) -> list[str]:
    """Return the model class names imported from the app's ``models`` module."""
    names: list[str] = []
    for line in source.splitlines():
        if line.startswith("from ") and ".models import " in line:
            names.extend(
                entry.strip() for entry in line.split("import ", 1)[1].split(",")
            )
    return names


def module_path(project_root: Path, app_label: str) -> Path:
    """Return the ``<app_label>/management/commands/<app_label>.py`` path."""
    return project_root / app_label / "management" / "commands" / f"{app_label}.py"
