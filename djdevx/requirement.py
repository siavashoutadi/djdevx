import typer

from .utils.print_console import console

from .utils.os_tools import is_tool_installed


app = typer.Typer()


@app.command()
def requirement():
    """
    Check the requirement for project creation.
    """
    console.step("Checking the requirement ...")

    uv_installed = is_tool_installed("uv")
    if uv_installed:
        console.info("✅ uv is installed")
    else:
        uv_link = "https://docs.astral.sh/uv/getting-started/installation/"
        console.info(f"❌ uv is not installed - [link={uv_link}]Install uv[/link]")

    git_installed = is_tool_installed("git")
    if git_installed:
        console.info("✅ git is installed")
    else:
        git_link = "https://git-scm.com/downloads"
        console.info(f"❌ git is not installed - [link={git_link}]Install git[/link]")

    docker_installed = is_tool_installed("docker")
    if docker_installed:
        console.info("✅ Docker is installed")
    else:
        docker_link = "https://docs.docker.com/get-docker/"
        console.info(
            f"❌ Docker is not installed - [link={docker_link}]Install Docker[/link]"
        )

    precommit_installed = is_tool_installed("pre-commit")
    if precommit_installed:
        console.info("✅ pre-commit is installed")
    else:
        console.info(
            "❌ pre-commit is not installed - Install it by 'uv tool install pre-commit'"
        )

    if docker_installed and uv_installed and git_installed:
        console.success("All requirements are met!")
    else:
        console.error(
            "Some requirements are missing. Please follow the links above to install them."
        )
        raise typer.Exit(code=1)
