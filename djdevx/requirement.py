import shutil
import typer

from djdevx.utils.print_console import (
    print_error,
    print_info,
    print_step,
    print_success,
)

app = typer.Typer()


@app.command()
def requirement():
    """
    Check the requirement for project creation.
    """
    print_step("Checking the requirement ...")

    uv_installed = is_installed("uv")
    if uv_installed:
        print_info("✅ uv is installed")
    else:
        uv_link = "https://docs.astral.sh/uv/getting-started/installation/"
        print_info(f"❌ uv is not installed - [link={uv_link}]Install uv[/link]")

    docker_installed = is_installed("docker")
    if docker_installed:
        print_info("✅ Docker is installed")
    else:
        docker_link = "https://docs.docker.com/get-docker/"
        print_info(
            f"❌ Docker is not installed - [link={docker_link}]Install Docker[/link]"
        )

    if docker_installed and uv_installed:
        print_success("All requirements are met!")
    else:
        print_error(
            "Some requirements are missing. Please follow the links above to install them."
        )
        raise typer.Exit(code=1)


def is_installed(command: str) -> bool:
    return shutil.which(command) is not None
