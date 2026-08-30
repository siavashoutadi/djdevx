"""ddx new — create a new Django project (flat structure, no backend_root)."""

import subprocess
import typer

from typing import Optional
from typing_extensions import Annotated
from pathlib import Path

from ..utils.console.print import print_console
from ..utils.console import prompts
from ..utils.project.secret_manager import SecretManager
from ..utils.project.pixi_runner import PixiRunner
from ..utils.generators import generate_random_password
from ..utils.templates.manager import TemplateManager
from ..utils.prek.prek import format_all_files_in_project
from ..requirement import verify as requirement_check

app = typer.Typer()

DJANGO_VERSION = "6.0"
DJANGO_PYTHON_VERSIONS: dict[str, list[str]] = {
    "6.0": ["3.12", "3.13", "3.14"],
}


@app.callback(invoke_without_command=True)
def new(
    project_name: Annotated[
        Optional[str],
        typer.Option(help="The name of the project"),
    ] = None,
    project_description: Annotated[
        Optional[str],
        typer.Option(help="The description of the project"),
    ] = None,
    project_directory: Annotated[
        Optional[Path],
        typer.Option(help="The directory to initialize the project in"),
    ] = None,
    python_version: Annotated[
        Optional[str],
        typer.Option(help="The minimum python version for the project"),
    ] = None,
    git_init: Annotated[
        bool,
        typer.Option(
            help="whether to initialize a git repository in the project directory"
        ),
    ] = True,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show full output of all commands"),
    ] = False,
):
    """Create a new Django project."""
    requirement_check()

    if project_name is None:
        project_name = prompts.text("Project name:", default="my-project")
        if project_name is None:
            raise typer.Abort()

    if project_description is None:
        project_description = prompts.text(
            "Project description:", default="My project is awesome"
        )
        if project_description is None:
            raise typer.Abort()

    if project_directory is None:
        raw = prompts.text("Directory to initialize the project in:", default=".")
        if raw is None:
            raise typer.Abort()
        project_directory = Path(raw)

    if python_version is None:
        python_version = prompts.select(
            "Select the minimum Python version",
            choices=DJANGO_PYTHON_VERSIONS[DJANGO_VERSION],
        )
        if python_version is None:
            raise typer.Abort()

    print_console.step("Initializing the project ...")

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir / "templates"
    dest_dir = project_directory.absolute()

    context = {
        "project_name": project_name,
        "project_description": project_description,
        "python_version": python_version,
        "django_version": DJANGO_VERSION,
    }

    template_manager = TemplateManager()
    template_manager.copy_templates(
        source_dir=source_dir, dest_dir=dest_dir, template_context=context
    )

    secret_manager = SecretManager(dest_dir)
    secret_manager.write_secret("secret_key", generate_random_password(length=64))

    install_dependencies(dest_dir)

    if git_init and not _is_git_repository(dest_dir):
        print_console.step("Initializing the git repository ...")
        _init_git(dest_dir, verbose=verbose)
        print_console.step_done("Git repository is initialized successfully.")

    format_all_files_in_project(dest_dir)

    print_console.step_done("Project is initialized successfully.")


def install_dependencies(project_root: Path):
    """Install Python dependencies in the specified directory."""
    pixi = PixiRunner(project_root=project_root)

    dependencies: list[str] = [
        f"django~={DJANGO_VERSION}.0",
        "django-typer",
        "ipython",
        "ipdb",
        "uvicorn",
        "pydantic-settings",
        "email-validator",
    ]
    print_console.step("Installing dependencies ...")
    for pkg in dependencies:
        pixi.add_package(pkg)
        print_console.ok(f"{PixiRunner._extract_package_name(pkg)} is installed")

    dev_dependencies: list[str] = [
        "factory_boy<4",
        "rich<16",
        "django-upgrade<2",
        "ruff<0.16",
        "prek>=0.4.14,<0.5",
    ]

    for pkg in dev_dependencies:
        pixi.add_package(pkg, feature="dev")
        print_console.ok(f"{PixiRunner._extract_package_name(pkg)} is installed")
    print_console.step_done("Dependencies are installed successfully.")


def _is_git_repository(project_dir: Path) -> bool:
    git_repository_dir = project_dir / ".git"
    return git_repository_dir.exists() and git_repository_dir.is_dir()


def _init_git(project_dir: Path, verbose: bool = False):
    git_commands: list[tuple[list[str], str]] = [
        (["git", "init", "--initial-branch=main"], "git init"),
        (["git", "add", "."], "git add"),
        (["git", "commit", "-m", "Initial commit"], "git commit"),
    ]
    for cmd, label in git_commands:
        if verbose:
            subprocess.check_call(cmd, cwd=project_dir)
        else:
            result = subprocess.run(
                cmd, cwd=project_dir, capture_output=True, text=True
            )
            if result.returncode != 0:
                print_console.error(result.stderr)
                result.check_returncode()
        print_console.ok(label)


if __name__ == "__main__":
    app()
