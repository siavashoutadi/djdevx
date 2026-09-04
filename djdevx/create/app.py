"""Create a new Django application."""

from pathlib import Path

from djdevx.core.paths import ProjectStructure
from djdevx.core.process import PixiRunner
from ..utils.templates.manager import TemplateManager


def startapp(application_name: str) -> None:
    """Create a new Django application."""
    structure = ProjectStructure()
    pixi_runner = PixiRunner(project_root=structure.root)
    pixi_runner.run_manage_command("startapp", application_name)

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir / "templates"

    template_manager = TemplateManager()
    template_manager.copy_templates(
        source_dir=source_dir,
        dest_dir=structure.root,
        template_context={"application_name": application_name},
    )
