import secrets
import shutil
import subprocess
import typer

from jinja2 import Environment, FileSystemLoader
from typing_extensions import Annotated
from pathlib import Path
from djdevx.utils.print_console import print_step, print_success

from djdevx.requirement import requirement

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
    git_init: Annotated[
        bool,
        typer.Option(
            help="whether to initialize a git repository in the project directory"
        ),
    ] = True,
):
    """
    Initialize the project
    """

    requirement()

    print_step("Initializing the project ...")

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "init"
    dest_dir = project_directory

    data = {
        "project_name": project_name,
        "project_description": project_description,
        "django_secret_key": generate_secret(),
    }

    copy_template_files(
        source_dir=source_dir,
        dest_dir=dest_dir,
        template_context=data,
    )

    print_success("Project is initialized successfully.")

    install_dependencies(dest_dir=dest_dir)

    if git_init and not is_git_repository():
        print_step("Initializing the git repository ...")
        init_git()

    update_precommit_hooks(dest_dir=dest_dir)


def generate_secret():
    return secrets.token_hex(32)


def install_dependencies(dest_dir: Path):
    dependencies: list[str] = [
        "django",
        "django-typer",
        "django-environ",
        "psycopg2-binary",
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


def copy_template_files(source_dir: Path, dest_dir: Path, template_context: dict):
    dest_dir.mkdir(parents=True, exist_ok=True)
    jinja_env = Environment(loader=FileSystemLoader(source_dir))

    for source_path in source_dir.rglob("*"):
        rel_path = source_path.relative_to(source_dir)
        dest_path = dest_dir / rel_path

        if source_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
        else:
            if source_path.suffix == ".j2":
                dest_path = dest_path.with_suffix("")

                template = jinja_env.get_template(str(rel_path))
                rendered_content = template.render(**template_context)
                rendered_content = rendered_content.rstrip("\n") + "\n"

                dest_path.write_text(rendered_content)
            else:
                shutil.copy2(source_path, dest_path)


def is_git_repository() -> bool:
    git_repository_dir = Path(".git")
    return git_repository_dir.exists() and git_repository_dir.is_dir()


def init_git():
    subprocess.check_call(["git", "init", "--initial-branch=main"])
    subprocess.check_call(["git", "add", "."])
    subprocess.check_call(["git", "commit", "-m", "Initial commit"])


if __name__ == "__main__":
    app()
