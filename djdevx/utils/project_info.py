import tomllib

from .project_files import get_pyproject_toml_path


def get_dependencies() -> list[str]:
    project_toml = get_pyproject_toml_path()
    with open(project_toml, "rb") as f:
        pyproject_data = tomllib.load(f)

    dependencies = pyproject_data.get("project", {}).get("dependencies", [])

    return dependencies


def has_dependency(dependency_name: str) -> bool:
    dependencies = get_dependencies()
    for dep in dependencies:
        if dep.startswith(dependency_name):
            return True
    return False
