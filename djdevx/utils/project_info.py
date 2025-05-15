import tomllib

from .project_files import get_pyproject_toml_path


def get_dependencies(group: str = "") -> list[str]:
    project_toml = get_pyproject_toml_path()
    with open(project_toml, "rb") as f:
        pyproject_data = tomllib.load(f)

    if group:
        return pyproject_data.get("dependency-groups", {}).get(group, [])

    return pyproject_data.get("project", {}).get("dependencies", [])


def has_dependency(dependency_name: str, group: str = "") -> bool:
    dependencies = get_dependencies(group)
    for dep in dependencies:
        name_without_version = (
            dep.split(">")[0].split("<")[0].split("=")[0].split("!")[0].strip()
        )

        name_without_extras = name_without_version.split("[")[0].strip()

        if name_without_extras == dependency_name:
            return True
    return False
