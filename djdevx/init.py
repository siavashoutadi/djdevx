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
    }

    copy_template_files(
        source_dir=source_dir,
        dest_dir=dest_dir,
        template_context=data,
    )

    print_success("Project is initialized successfully.")

    print_step("Installing Django ...")

    subprocess.check_call(["uv", "add", "django"], cwd=dest_dir)

    print_success("Django is installed successfully.")

    if git_init and not is_git_repository():
        print_step("Initializing the git repository ...")
        init_git()


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
