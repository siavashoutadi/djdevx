import typer

from .utils.console.print import print_console
from .utils.system.tools import system_tools


app = typer.Typer()


@app.command()
def requirement():
    """
    Check the requirement for project creation.
    """
    print_console.step("Checking the requirement ...")

    pixi_installed = system_tools.is_tool_installed("pixi")
    if pixi_installed:
        print_console.info("✅ pixi is installed")
    else:
        pixi_link = "https://pixi.sh"
        print_console.info(
            f"❌ pixi is not installed - [link={pixi_link}]Install pixi[/link]"
        )

    git_installed = system_tools.is_tool_installed("git")
    if git_installed:
        print_console.info("✅ git is installed")
    else:
        git_link = "https://git-scm.com/downloads"
        print_console.info(
            f"❌ git is not installed - [link={git_link}]Install git[/link]"
        )

    docker_installed = system_tools.is_tool_installed("docker")
    if docker_installed:
        print_console.info("✅ Docker is installed")
    else:
        docker_link = "https://docs.docker.com/get-docker/"
        print_console.info(
            f"❌ Docker is not installed - [link={docker_link}]Install Docker[/link]"
        )

    prek_installed = system_tools.is_tool_installed("prek")
    if prek_installed:
        print_console.info("✅ prek is installed")
    else:
        print_console.info(
            "❌ prek is not installed - Install it by 'pipx install prek' or 'uv tool install prek'"
        )

    if docker_installed and pixi_installed and git_installed:
        print_console.success("All requirements are met!")
    else:
        print_console.error(
            "Some requirements are missing. Please follow the links above to install them."
        )
        raise typer.Exit(code=1)
