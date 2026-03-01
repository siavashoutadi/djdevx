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

    uv_installed = system_tools.is_tool_installed("uv")
    if uv_installed:
        print_console.info("✅ uv is installed")
    else:
        uv_link = "https://docs.astral.sh/uv/getting-started/installation/"
        print_console.info(
            f"❌ uv is not installed - [link={uv_link}]Install uv[/link]"
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

    precommit_installed = system_tools.is_tool_installed("pre-commit")
    if precommit_installed:
        print_console.info("✅ pre-commit is installed")
    else:
        print_console.info(
            "❌ pre-commit is not installed - Install it by 'uv tool install pre-commit'"
        )

    if docker_installed and uv_installed and git_installed:
        print_console.success("All requirements are met!")
    else:
        print_console.error(
            "Some requirements are missing. Please follow the links above to install them."
        )
        raise typer.Exit(code=1)
