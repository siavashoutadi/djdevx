import subprocess
import typer

from typing_extensions import Annotated
from pathlib import Path

from ...utils.console.print import print_console
from ...utils.django.secret_manager import SecretManager
from ...utils.django.uv_runner import UvRunner
from ...utils.generators import generate_random_password
from ...utils.templates.manager import TemplateManager
from ...requirement import requirement

app = typer.Typer(no_args_is_help=True)

DJANGO_VERSION = "6.0"


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

    print_console.step("Initializing the project ...")

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir / ".." / ".." / "templates" / "new" / "backend" / "django"
    dest_dir = project_directory.absolute()
    backend_root_path = dest_dir / backend_root

    data = {
        "project_name": project_name,
        "project_description": project_description,
        "python_version": python_version,
        "django_version": DJANGO_VERSION,
        "backend_root": backend_root,
    }

    template_manager = TemplateManager()
    template_manager.copy_templates(
        source_dir=source_dir, dest_dir=dest_dir, template_context=data
    )

    secret_manager = SecretManager(backend_root_path)
    secret_manager.write_secret("secret_key", generate_random_password(length=64))

    install_dependencies(backend_root_path)

    if git_init and not is_git_repository(dest_dir):
        print_console.step("Initializing the git repository ...")
        init_git(dest_dir)

    update_prek_hooks(
        backend_root=backend_root_path, project_dir=dest_dir, git_init=git_init
    )

    print_console.success("Project is initialized successfully.")


def install_dependencies(backend_root: Path):
    """Install Python dependencies in the specified directory."""
    uv = UvRunner(backend_root=backend_root)

    dependencies: list[str] = [
        f"django~={DJANGO_VERSION}.0",
        "django-typer",
        "ipython",
        "ipdb",
        "uvicorn",
        "pydantic-settings",
        "email-validator",
    ]
    for pkg in dependencies:
        print_console.step(f"Installing {pkg} ...")
        uv.add_package(pkg)
        print_console.success(f"{pkg} is installed successfully.")

    dev_dependencies: list[str] = [
        "factory_boy",
        "rich",
        "prek",
        "django-upgrade",
        "ruff",
    ]

    for pkg in dev_dependencies:
        print_console.step(f"Installing {pkg} ...")
        uv.add_package(pkg, group="dev")
        print_console.success(f"{pkg} is installed successfully.")


def update_prek_hooks(backend_root: Path, project_dir: Path, git_init: bool):
    print_console.step("Updating prek hooks ...")
    uv = UvRunner(backend_root=backend_root)
    uv.run_uv_command("run", "prek", "update")
    if git_init and is_git_repository(project_dir):
        subprocess.check_call(["git", "add", "."], cwd=project_dir)
        subprocess.check_call(
            ["git", "commit", "--amend", "--no-edit"], cwd=project_dir
        )


def is_git_repository(project_dir: Path) -> bool:
    git_repository_dir = project_dir / ".git"
    return git_repository_dir.exists() and git_repository_dir.is_dir()


def init_git(project_dir: Path):
    subprocess.check_call(["git", "init", "--initial-branch=main"], cwd=project_dir)
    subprocess.check_call(["git", "add", "."], cwd=project_dir)
    subprocess.check_call(["git", "commit", "-m", "Initial commit"], cwd=project_dir)


if __name__ == "__main__":
    app()
