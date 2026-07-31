"""Requirement check — verifies system tools are installed."""

import typer

from ..utils.console.print import print_console
from ..utils.system.tools import system_tools


app = typer.Typer(no_args_is_help=True)


@app.command()
def verify():
    """Check the requirements for project creation."""
    print_console.step("Checking the requirements ...")

    pixi_installed = system_tools.is_tool_installed("pixi")
    if pixi_installed:
        print_console.ok("pixi is installed")
    else:
        print_console.fail(
            "pixi is not installed - https://pixi.prefix.dev/latest/installation/"
        )

    git_installed = system_tools.is_tool_installed("git")
    if git_installed:
        print_console.ok("git is installed")
    else:
        print_console.fail("git is not installed - https://git-scm.com/downloads")

    docker_installed = system_tools.is_tool_installed("docker")
    if docker_installed:
        print_console.ok("Docker is installed")
    else:
        print_console.fail(
            "Docker is not installed - https://docs.docker.com/get-docker/"
        )

    if docker_installed and pixi_installed and git_installed:
        print_console.step_done("All requirements are met!")
    else:
        print_console.fail(
            "Some requirements are missing. Please follow the links above to install them."
        )
        raise typer.Exit(code=1)
