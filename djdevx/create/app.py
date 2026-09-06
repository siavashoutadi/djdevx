"""Create a new Django application."""

from pathlib import Path

import typer

from djdevx.core.console import print_console
from djdevx.core.paths import ProjectStructure
from djdevx.core.process import PixiRunner
from ..utils.templates.manager import TemplateManager


def startapp(application_name: str) -> None:
    """Create a new Django application."""
    structure = ProjectStructure()
    pixi_runner = PixiRunner(project_root=structure.root)
    print_console.step(f"Creating application {application_name!r}")
    result = pixi_runner.run_interactive(
        "run", "python", "manage.py", "startapp", application_name
    )
    if result.returncode != 0:
        print_console.error(
            f"Could not create application {application_name!r} "
            f"(exit code {result.returncode})."
        )
        raise typer.Exit(code=result.returncode)

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir / "templates"

    template_manager = TemplateManager()
    template_manager.copy_templates(
        source_dir=source_dir,
        dest_dir=structure.root,
        template_context={"application_name": application_name},
    )
    print_console.step_done(f"Application {application_name!r} created")
