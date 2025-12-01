import ast
import typer
import warnings

from pathlib import Path
from typing import List, Dict, Any, Optional

from .print_console import console
from .djdevx_config import DjdevxConfig
from .file_operations import TemplateManager


def get_pyproject_toml_path() -> Path:
    warnings.warn(
        "get_pyproject_toml_path is deprecated. Use DjangoProjectManager().pyproject_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    config = DjdevxConfig()
    backend_root = config.django_backend_root
    return Path.joinpath(backend_root, "pyproject.toml")


def get_django_project_path() -> Path:
    warnings.warn(
        "get_django_project_path is deprecated. Use DjangoProjectManager().project_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_pyproject_toml_path().parent


def get_django_settings_path() -> Path:
    warnings.warn(
        "get_django_settings_path is deprecated. Use DjangoProjectManager().settings_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Path.joinpath(get_django_project_path(), "settings")


def get_packages_settings_path() -> Path:
    warnings.warn(
        "get_packages_settings_path is deprecated. Use DjangoProjectManager().packages_settings_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Path.joinpath(get_django_settings_path(), "packages")


def get_django_url_path() -> Path:
    warnings.warn(
        "get_django_url_path is deprecated. Use DjangoProjectManager().urls_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Path.joinpath(get_django_project_path(), "urls")


def get_django_ws_url_path() -> Path:
    warnings.warn(
        "get_django_ws_url_path is deprecated. Use DjangoProjectManager().ws_urls_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Path.joinpath(get_django_project_path(), "ws_urls")


def get_django_packages_url_path() -> Path:
    warnings.warn(
        "get_django_packages_url_path is deprecated. Use DjangoProjectManager().packages_urls_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Path.joinpath(get_django_url_path(), "packages")


def get_django_base_template_path() -> Path:
    warnings.warn(
        "get_django_base_template_path is deprecated. Use DjangoProjectManager().base_template_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Path.joinpath(get_django_project_path(), "templates", "_base.html")


def get_django_gitignore_path() -> Path:
    return Path.joinpath(get_django_project_path(), ".gitignore")


def get_django_docker_file_path() -> Path:
    return Path.joinpath(get_django_project_path(), "Dockerfile")


def get_django_models_path(application_name: str) -> Path:
    """
    Get the path to models.py for a given application
    """
    return Path.joinpath(get_django_project_path(), application_name, "models.py")


def get_django_admin_path(application_name: str) -> Path:
    """
    Get the path to admin.py for a given application
    """
    return Path.joinpath(get_django_project_path(), application_name, "admin.py")


def get_django_static_path() -> Path:
    """
    Get the path to the static directory
    """
    return Path.joinpath(get_django_project_path(), "static")


def get_django_css_path() -> Path:
    warnings.warn(
        "get_django_css_path is deprecated. Use DjangoProjectManager().css_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Path.joinpath(get_django_static_path(), "css")


def get_django_js_path() -> Path:
    warnings.warn(
        "get_django_js_path is deprecated. Use DjangoProjectManager().js_path instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Path.joinpath(get_django_static_path(), "js")


def copy_template_files(
    source_dir: Path,
    dest_dir: Path,
    template_context: dict,
    excluede_files: List[Path] = [],
):
    """Legacy wrapper. Use DjangoProjectManager().copy_templates() instead."""
    warnings.warn(
        "copy_template_files is deprecated. Use DjangoProjectManager().copy_templates() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    template_manager = TemplateManager()
    template_manager.copy_templates(
        source_dir=source_dir,
        dest_dir=dest_dir,
        template_context=template_context,
        exclude_files=excluede_files,
    )


def copy_template_file(
    source_file: Path, dest_dir: Path, template_context: dict
) -> Path:
    """Legacy wrapper. Use DjangoProjectManager().copy_template() instead."""
    warnings.warn(
        "copy_template_file is deprecated. Use DjangoProjectManager().copy_template() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    template_manager = TemplateManager()
    return template_manager.copy_template(
        source_file=source_file,
        dest_dir=dest_dir,
        template_context=template_context,
    )


def is_django_backend_exist_or_raise():
    warnings.warn(
        "is_django_backend_exist_or_raise is deprecated. Use DjangoProjectManager().validate_django_project() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if not Path.exists(get_django_project_path()):
        console.error(
            "Could not find pyproject.toml. Are you running from the project directory?"
        )
        raise typer.Exit(code=1)


def get_django_models(app_name):
    """Parse models.py file and extract model information."""
    warnings.warn(
        "get_django_models is deprecated. Use DjangoProjectManager().get_models() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    models_file = get_django_models_path(app_name)

    if not models_file.exists():
        console.error(f"Could not find {models_file}")
        raise typer.Exit(code=1)

    try:
        with open(models_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(models_file))
    except SyntaxError as e:
        console.error(f"Syntax error in {models_file}: {e}")
        raise typer.Exit(code=1)

    visitor = ModelVisitor()
    visitor.visit(tree)

    return visitor.models


def get_project_root_dir() -> Path:
    """Legacy wrapper. Use DjdevxConfig().project_root_dir instead."""
    config = DjdevxConfig()
    return config.project_root_dir


def get_devcontainer_path() -> Path:
    """Legacy wrapper. Use DjdevxConfig().devcontainer_path instead."""
    config = DjdevxConfig()
    return config.devcontainer_path


def get_devcontainer_env_path() -> Path:
    """Legacy wrapper. Use DjdevxConfig().devcontainer_env_path instead."""
    config = DjdevxConfig()
    return config.devcontainer_env_path


def get_devcontainer_env_devcontainer_path() -> Path:
    """Legacy wrapper. Use DjdevxConfig().devcontainer_env_devcontainer_path instead."""
    config = DjdevxConfig()
    return config.devcontainer_env_devcontainer_path


def add_env_varibles(key: str, value: str, file_path: Path | None = None):
    """Legacy wrapper. Use DjangoProjectManager().add_env_variable() instead."""
    warnings.warn(
        "add_env_varibles is deprecated. Use DjangoProjectManager().add_env_variable() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if file_path is None:
        file_path = get_devcontainer_env_devcontainer_path()
    remove_env_varibles(key, file_path)
    with open(file_path, "a") as f:
        f.write(f"{key}={value}\n")


def remove_env_varibles(key: str, file_path: Path | None = None):
    """Legacy wrapper. Use DjangoProjectManager().remove_env_variable() instead."""
    warnings.warn(
        "remove_env_varibles is deprecated. Use DjangoProjectManager().remove_env_variable() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if file_path is None:
        file_path = get_devcontainer_env_devcontainer_path()
    template_manager = TemplateManager()
    template_manager.remove_lines_from_file(file_path, [f"{key}="])


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
