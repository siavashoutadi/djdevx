import shutil
import typer
import fileinput

from pathlib import Path


from jinja2 import Environment, FileSystemLoader

from .print_console import print_error


def get_pyproject_toml_path() -> Path:
    project_dir = Path.cwd()
    return Path.joinpath(project_dir, "pyproject.toml")


def get_project_path() -> Path:
    return get_pyproject_toml_path().parent


def get_settings_path() -> Path:
    return Path.joinpath(get_project_path(), "settings")


def get_packages_settings_path() -> Path:
    return Path.joinpath(get_settings_path(), "packages")


def get_url_path() -> Path:
    return Path.joinpath(get_project_path(), "urls")


def get_packages_url_path() -> Path:
    return Path.joinpath(get_url_path(), "packages")


def get_base_template_path() -> Path:
    return Path.joinpath(get_project_path(), "templates", "_base.html")


def get_gitignore_path() -> Path:
    return Path.joinpath(get_project_path(), ".gitignore")


def get_docker_file_path() -> Path:
    return Path.joinpath(get_project_path(), "Dockerfile")


def get_devcontainer_path() -> Path:
    return Path.joinpath(get_project_path(), ".devcontainer")


def get_devcontainer_env_path() -> Path:
    return Path.joinpath(get_devcontainer_path(), ".env")


def get_devcontainer_env_devcontainer_path() -> Path:
    return Path.joinpath(get_devcontainer_env_path(), "devcontainer")


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


def is_project_exists_or_raise():
    if not Path.exists(get_project_path()):
        print_error(
            "Could not find pyproject.toml. Are you running from the project directory?"
        )
        raise typer.Abort()


def add_env_varibles(
    key: str, value: str, file_path: Path = get_devcontainer_env_devcontainer_path()
):
    remove_env_varibles(key)
    with open(file_path, "a") as f:
        f.write(f"{key}={value}\n")


def remove_env_varibles(
    key: str, file_path: Path = get_devcontainer_env_devcontainer_path()
):
    with fileinput.input(files=[file_path], inplace=True) as f:
        for line in f:
            if not line.startswith(f"{key}="):
                print(line, end="")
