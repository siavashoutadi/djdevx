import ast
import shutil
import typer
import fileinput

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Any, Optional

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


def get_ws_url_path() -> Path:
    return Path.joinpath(get_project_path(), "ws_urls")


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


def get_models_path(application_name: str) -> Path:
    """
    Get the path to models.py for a given application
    """
    return Path.joinpath(get_project_path(), application_name, "models.py")


def get_admin_path(application_name: str) -> Path:
    """
    Get the path to admin.py for a given application
    """
    return Path.joinpath(get_project_path(), application_name, "admin.py")


def get_static_path() -> Path:
    """
    Get the path to the static directory
    """
    return Path.joinpath(get_project_path(), "static")


def get_css_path() -> Path:
    """
    Get the path to the CSS directory
    """
    return Path.joinpath(get_static_path(), "css")


def get_js_path() -> Path:
    """
    Get the path to the JavaScript directory
    """
    return Path.joinpath(get_static_path(), "js")


def render_template_string(path: str, template_context: dict) -> str:
    if "{{" in path or "{%" in path:
        template = Environment().from_string(path)
        return template.render(**template_context)
    return path


def copy_template_files(
    source_dir: Path,
    dest_dir: Path,
    template_context: dict,
    excluede_files: List[Path] = [],
):
    dest_dir.mkdir(parents=True, exist_ok=True)
    jinja_env = Environment(loader=FileSystemLoader(source_dir))

    for source_path in source_dir.rglob("*"):
        if any(source_path.match(str(exclude)) for exclude in excluede_files):
            continue

        rel_path = source_path.relative_to(source_dir)

        rendered_parts = [
            render_template_string(part, template_context) for part in rel_path.parts
        ]
        dest_path = dest_dir / Path(*rendered_parts)

        if source_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
        else:
            if source_path.suffix == ".j2":
                filename = render_template_string(dest_path.stem, template_context)
                dest_path = dest_path.parent / filename
                template = jinja_env.get_template(str(rel_path))
                rendered_content = template.render(**template_context)
                rendered_content = rendered_content.rstrip("\n") + "\n"

                dest_path.write_text(rendered_content)
            else:
                filename = render_template_string(dest_path.name, template_context)
                dest_path = dest_path.parent / filename

                shutil.copy2(source_path, dest_path)


def copy_template_file(
    source_file: Path, dest_dir: Path, template_context: dict
) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)

    jinja_env = Environment(loader=FileSystemLoader(source_file.parent))

    filename = render_template_string(source_file.name, template_context)
    dest_path = dest_dir / filename

    if source_file.suffix == ".j2":
        template = jinja_env.get_template(source_file.name)
        rendered_content = template.render(**template_context)
        rendered_content = rendered_content.rstrip("\n") + "\n"

        if dest_path.suffix == ".j2":
            dest_path = dest_path.with_suffix("")

        dest_path.write_text(rendered_content)
    else:
        shutil.copy2(source_file, dest_path)

    return dest_path


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


def get_models(app_name):
    """Parse models.py file and extract model information."""

    models_file = get_models_path(app_name)

    if not models_file.exists():
        print_error(f"Could not find {models_file}")
        raise typer.Exit(code=1)

    try:
        with open(models_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(models_file))
    except SyntaxError as e:
        print_error(f"Syntax error in {models_file}: {e}")
        raise typer.Exit(code=1)

    visitor = ModelVisitor()
    visitor.visit(tree)

    return visitor.models


class ModelVisitor(ast.NodeVisitor):
    """AST visitor to extract Django model information."""

    def __init__(self) -> None:
        self.models: List[Dict[str, Any]] = []
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to find Django models."""
        # Check if class inherits from models.Model
        is_model: bool = any(
            (
                isinstance(base, ast.Attribute)
                and isinstance(base.value, ast.Name)
                and base.value.id == "models"
                and base.attr == "Model"
            )
            or (isinstance(base, ast.Name) and base.id == "Model")
            for base in node.bases
        )

        if is_model:
            model_info: Dict[str, Any] = {"name": node.name, "fields": [], "meta": {}}

            # Extract fields
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            field_info: Optional[Dict[str, Any]] = (
                                self._extract_field_info(target.id, item.value)
                            )
                            if field_info:
                                model_info["fields"].append(field_info)

                # Extract Meta class
                elif isinstance(item, ast.ClassDef) and item.name == "Meta":
                    model_info["meta"] = self._extract_meta(item)

            self.models.append(model_info)

        self.generic_visit(node)

    def _extract_field_info(
        self, name: str, value: ast.expr
    ) -> Optional[Dict[str, Any]]:
        """Extract field type and properties from assignment."""
        # Skip managers and non-field attributes
        if name in ["objects", "published"] or name.startswith("_"):
            return None

        field_type: Optional[str] = None
        is_relation: bool = False
        related_model: Optional[str] = None

        if isinstance(value, ast.Call):
            if isinstance(value.func, ast.Attribute):
                # models.CharField(), models.ForeignKey(), etc.
                if (
                    isinstance(value.func.value, ast.Name)
                    and value.func.value.id == "models"
                ):
                    field_type = value.func.attr
                else:
                    # Other field types like RichTextUploadingField
                    field_type = (
                        value.func.attr
                        if isinstance(value.func, ast.Attribute)
                        else None
                    )
            elif isinstance(value.func, ast.Name):
                # Direct field class like TaggableManager()
                field_type = value.func.id

            # Check if it's a relation field
            if field_type in ["ForeignKey", "OneToOneField", "ManyToManyField"]:
                is_relation = True
                # Try to extract related model name
                if value.args:
                    first_arg: ast.expr = value.args[0]
                    if isinstance(first_arg, ast.Name):
                        related_model = first_arg.id
                    elif isinstance(first_arg, ast.Call):
                        # get_user_model() case
                        if isinstance(first_arg.func, ast.Name):
                            related_model = "User"  # Assume User model

        if field_type:
            return {
                "name": name,
                "type": field_type,
                "is_relation": is_relation,
                "related_model": related_model,
            }

        return None

    def _extract_meta(self, meta_class: ast.ClassDef) -> Dict[str, ast.expr]:
        """Extract Meta class information."""
        meta_info: Dict[str, ast.expr] = {}
        for item in meta_class.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        meta_info[target.id] = item.value
        return meta_info
