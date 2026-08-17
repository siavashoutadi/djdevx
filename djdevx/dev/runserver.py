"""ddx dev runserver — run the correct dev server command, no checks."""

import typer

from ..utils.console.print import print_console
from ..utils.project.pixi_runner import PixiRunner
from ..utils.tracking import ProjectTracking, Section


def server_command(runner: PixiRunner) -> list[str]:
    """Resolve the pixi args that start the dev server (tailwind-aware)."""
    tracking = ProjectTracking(runner.project_root)
    if tracking.is_installed(Section.PACKAGES, "django-tailwind-cli"):
        print_console.step_done(
            "Detected django-tailwind-cli, using tailwind runserver"
        )
        return ["run", "python", "manage.py", "tailwind", "runserver"]
    print_console.step_done("Using standard Django runserver on 0.0.0.0:8000")
    return ["run", "python", "manage.py", "runserver", "0.0.0.0:8000"]


def runserver(ctx: typer.Context) -> None:
    """Run the dev server (tailwind-aware).

    Any additional arguments (including ``--help``) are forwarded to the
    underlying Django ``runserver`` command.
    """
    from ..utils.services import resolve_dev_services

    services = resolve_dev_services()
    if services:
        print_console.step("Setting service port environment variables...")
        for service in services:
            service._set_port_env()

    runner = PixiRunner()
    runner.run_interactive(*server_command(runner), *ctx.args)
