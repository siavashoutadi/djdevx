import os
import secrets
import subprocess
import typer

from typing_extensions import Annotated
from pathlib import Path

from .utils.os_tools import is_tool_installed

from .utils.print_console import print_step, print_success, print_warning
from .utils.project_files import copy_template_files
from .requirement import requirement
from .packages.django_tailwind_cli import install as install_django_tailwind_cli

app = typer.Typer()


@app.command()
def init(
    project_name: Annotated[
        str,
        typer.Option(
            help="The name of the project", prompt="Please enter the project name"
        ),
    ] = "my-project",
    project_description: Annotated[
        str,
        typer.Option(
            help="The description of the project",
            prompt="Please enter the project description",
        ),
    ] = "My project is awesome",
    project_directory: Annotated[
        Path,
        typer.Option(
            help="The directory to initialize the project in",
            prompt="Please enter directory to initialize the project in",
        ),
    ] = Path("."),
    python_version: Annotated[
        str,
        typer.Option(
            help="The minimum python version for the project",
            prompt="Please enter the minimum python version for the project",
        ),
    ] = "3.14",
    git_init: Annotated[
        bool,
        typer.Option(
            help="whether to initialize a git repository in the project directory"
        ),
    ] = True,
    skip_devbox: Annotated[
        bool,
        typer.Option(help="whether to skip devbox initialization"),
    ] = True,
    skip_biome: Annotated[
        bool,
        typer.Option(help="whether to skip biome initialization"),
    ] = True,
):
    """
    Initialize the project
    """

    requirement()

    print_step("Initializing the project ...")

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir / "templates" / "init"
    project_directory = project_directory.absolute()
    dest_dir = project_directory

    data = {
        "project_name": project_name,
        "project_description": project_description,
        "django_secret_key": generate_secret(),
        "python_version": python_version,
        "skip_biome": skip_biome,
    }

    exclude_files: list[Path] = []

    if skip_devbox:
        exclude_files.append(source_dir / "devbox.json.j2")
        exclude_files.append(source_dir / "devbox.d" / ".env.j2")

    if skip_biome:
        exclude_files.append(source_dir / "biome.jsonc")

    copy_template_files(
        source_dir=source_dir,
        dest_dir=dest_dir,
        template_context=data,
        excluede_files=exclude_files,
    )

    install_dependencies(dest_dir=dest_dir)

    os.chdir(project_directory)
    install_django_tailwind_cli()

    if not skip_devbox:
        devbox_init(project_directory)

    if git_init and not is_git_repository(project_directory):
        print_step("Initializing the git repository ...")
        init_git(project_directory)

    update_precommit_hooks(dest_dir=dest_dir)

    print_success("Project is initialized successfully.")


def generate_secret():
    return secrets.token_hex(32)


def install_dependencies(dest_dir: Path):
    dependencies: list[str] = [
        "django",
        "django-typer",
        "django-environ",
        "psycopg2-binary",
        "django-redis",
        "ipython",
        "ipdb",
        "uvicorn",
    ]
    for pkg in dependencies:
        print_step(f"Installing {pkg} ...")
        subprocess.check_call(["uv", "add", pkg], cwd=dest_dir)
        print_success(f"{pkg} is installed successfully.")

    dev_dependencies: list[str] = [
        "factory_boy",
        "rich",
        "pre-commit",
        "django-upgrade",
        "ruff",
    ]

    for pkg in dev_dependencies:
        print_step(f"Installing {pkg} ...")
        subprocess.check_call(["uv", "add", "--dev", pkg], cwd=dest_dir)
        print_success(f"{pkg} is installed successfully.")


def update_precommit_hooks(dest_dir):
    print_step("Updating pre-commit hooks ...")
    subprocess.check_call(["uv", "run", "pre-commit", "autoupdate"], cwd=dest_dir)
    subprocess.check_call(["git", "add", "."], cwd=dest_dir)
    subprocess.check_call(["git", "commit", "--amend", "--no-edit"], cwd=dest_dir)


def is_git_repository(project_dir: Path) -> bool:
    git_repository_dir = project_dir / ".git"
    return git_repository_dir.exists() and git_repository_dir.is_dir()


def init_git(project_dir: Path):
    subprocess.check_call(["git", "init", "--initial-branch=main"], cwd=project_dir)
    subprocess.check_call(["git", "add", "."], cwd=project_dir)
    subprocess.check_call(["git", "commit", "-m", "Initial commit"], cwd=project_dir)


def devbox_init(project_dir: Path):
    print_step("Updating devbox packages ...")
    if not is_tool_installed("devbox"):
        print_warning("Devbox is not installed. Skip Updating the packages.")
        return

    subprocess.check_call(["devbox", "update"], cwd=project_dir)

    print_success("Packages are updated successfully.\n")


if __name__ == "__main__":
    app()
