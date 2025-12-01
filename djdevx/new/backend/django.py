import secrets
import subprocess
import typer

from typing_extensions import Annotated
from pathlib import Path

from ...utils.print_console import console
from ...utils.file_operations import TemplateManager
from ...utils.django.uv_runner import UvRunner
from ...requirement import requirement

app = typer.Typer(no_args_is_help=True)

DJANGO_VERSION = "5.2"


@app.command()
def django(
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
    backend_root: Annotated[
        str,
        typer.Option(
            help="Backend root directory name",
            prompt="Please enter backend root directory name",
        ),
    ] = "backend",
    git_init: Annotated[
        bool,
        typer.Option(
            help="whether to initialize a git repository in the project directory"
        ),
    ] = True,
):
    """
    Create a new django project
    """

    requirement()

    console.step("Initializing the project ...")

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir / ".." / ".." / "templates" / "new" / "backend" / "django"
    dest_dir = project_directory.absolute()
    backend_root_path = dest_dir / backend_root

    data = {
        "project_name": project_name,
        "project_description": project_description,
        "django_secret_key": generate_secret(),
        "python_version": python_version,
        "django_version": DJANGO_VERSION,
        "backend_root": backend_root,
    }

    template_manager = TemplateManager()
    template_manager.copy_templates(
        source_dir=source_dir, dest_dir=dest_dir, template_context=data
    )

    install_dependencies(backend_root_path)

    if git_init and not is_git_repository(dest_dir):
        console.step("Initializing the git repository ...")
        init_git(dest_dir)

    update_precommit_hooks(backend_root=backend_root_path, project_dir=dest_dir)

    console.success("Project is initialized successfully.")


def generate_secret():
    return secrets.token_hex(32)


def install_dependencies(backend_root: Path):
    """Install Python dependencies in the specified directory."""
    uv = UvRunner(backend_root=backend_root)

    dependencies: list[str] = [
        f"django~={DJANGO_VERSION}.0",
        "django-typer",
        "django-environ",
        "psycopg2-binary",
        "django-redis",
        "ipython",
        "ipdb",
        "uvicorn",
    ]
    for pkg in dependencies:
        console.step(f"Installing {pkg} ...")
        uv.add_package(pkg)
        console.success(f"{pkg} is installed successfully.")

    dev_dependencies: list[str] = [
        "factory_boy",
        "rich",
        "pre-commit",
        "django-upgrade",
        "ruff",
    ]

    for pkg in dev_dependencies:
        console.step(f"Installing {pkg} ...")
        uv.add_package(pkg, group="dev")
        console.success(f"{pkg} is installed successfully.")


def update_precommit_hooks(backend_root: Path, project_dir: Path):
    console.step("Updating pre-commit hooks ...")
    uv = UvRunner(backend_root=backend_root)
    uv.run_uv_command("run", "pre-commit", "autoupdate")
    subprocess.check_call(["git", "add", "."], cwd=project_dir)
    subprocess.check_call(["git", "commit", "--amend", "--no-edit"], cwd=project_dir)


def is_git_repository(project_dir: Path) -> bool:
    git_repository_dir = project_dir / ".git"
    return git_repository_dir.exists() and git_repository_dir.is_dir()


def init_git(project_dir: Path):
    subprocess.check_call(["git", "init", "--initial-branch=main"], cwd=project_dir)
    subprocess.check_call(["git", "add", "."], cwd=project_dir)
    subprocess.check_call(["git", "commit", "-m", "Initial commit"], cwd=project_dir)


if __name__ == "__main__":
    app()
