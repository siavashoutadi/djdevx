"""Create CLI — create Django apps and components."""

import typer
from typing_extensions import Annotated

from ..utils.console import prompts
from .app import startapp as _startapp_cmd
from .base_model import base_model as _base_model_cmd
from .base_model import validate_app_name as _validate_app_name
from .base_model import validate_class_name as _validate_class_name
from .factory_boy import factory as _factory_cmd
from .seed_command import seed_command as _seed_command_cmd

app = typer.Typer(no_args_is_help=True)


@app.command("app")
def create_app(
    name: Annotated[
        str | None,
        typer.Option(help="Application name"),
    ] = None,
) -> None:
    """Create a new Django application."""
    if name is None:
        name = prompts.text("Please enter the application name")
        if name is None:
            raise typer.Abort()
    if not name.strip():
        raise typer.BadParameter("An application name is required.")
    _startapp_cmd(name)


@app.command("base-model")
def create_base_model(
    app_name: Annotated[
        str,
        typer.Option(
            "--app",
            help="Target Django app name",
            callback=_validate_app_name,
        ),
    ] = "core",
    class_name: Annotated[
        str,
        typer.Option(
            "--class-name",
            help="Abstract base model class name",
            callback=_validate_class_name,
        ),
    ] = "TimeStampedModel",
) -> None:
    """Create a timestamped abstract base model."""
    _base_model_cmd(app_name=app_name, class_name=class_name)


@app.command("factory-boy")
def create_factory(
    models: Annotated[
        list[str] | None,
        typer.Option(
            "--model",
            help="Model (app_label.ModelName) to generate a factory boy factory for",
        ),
    ] = None,
) -> None:
    """Generate a factory-boy factory for one or more project models.

    Re-running the command refreshes existing factories with any fields the
    models gained since the last run (new fields, many-to-many hooks, unique
    attributes), preserving manual edits.
    """
    _factory_cmd(models)


@app.command("seed-command")
def create_seed_command(
    models: Annotated[
        list[str] | None,
        typer.Option(
            "--model",
            help="Model (app_label.ModelName) to generate a seed management command for",
        ),
    ] = None,
) -> None:
    """Generate a management command that seeds project models via factory-boy.

    Writes a ``management/commands/app.py`` module per app for the chosen
    models, each exposing seed and clean subcommands per model (one pair per
    model, suffixed with the lowercased model name) backed by the app factories. Factory-boy factories are generated first when
    missing, so the seed command and the factories stay connected.
    """
    _seed_command_cmd(models)
