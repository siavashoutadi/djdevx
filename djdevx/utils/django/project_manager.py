import ast
import tomllib
import typer
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..print_console import console
from ..djdevx_config import DjdevxConfig
from ..file_operations import TemplateManager


class DjangoProjectManager:
    """
    Complete Django project management including paths, templates, and environment.
    Centralizes all Django-specific file operations and project structure management.
    """

    def __init__(self):
        """Initialize and validate Django project."""
        self._config = DjdevxConfig()
        self._template_manager = TemplateManager()
        self.validate_django_project()

    def validate_django_project(self) -> None:
        """Validate that this is a Django project managed by djdevx."""
        if not self.project_path.exists():
            console.error(
                "Could not find pyproject.toml. Are you running from the project directory?"
            )
            raise typer.Exit(code=1)

    # Path Properties
    @property
    def pyproject_path(self) -> Path:
        """Get pyproject.toml path."""
        return Path.joinpath(self._config.django_backend_root, "pyproject.toml")

    @property
    def project_path(self) -> Path:
        """Get Django project root path."""
        return self.pyproject_path.parent

    @property
    def settings_path(self) -> Path:
        """Get settings directory path."""
        return Path.joinpath(self.project_path, "settings")

    @property
    def packages_settings_path(self) -> Path:
        """Get packages settings directory path."""
        return Path.joinpath(self.settings_path, "packages")

    @property
    def urls_path(self) -> Path:
        """Get URLs directory path."""
        return Path.joinpath(self.project_path, "urls")

    @property
    def ws_urls_path(self) -> Path:
        """Get WebSocket URLs directory path."""
        return Path.joinpath(self.project_path, "ws_urls")

    @property
    def packages_urls_path(self) -> Path:
        """Get packages URLs directory path."""
        return Path.joinpath(self.urls_path, "packages")

    @property
    def base_template_path(self) -> Path:
        """Get base template path."""
        return Path.joinpath(self.project_path, "templates", "_base.html")

    @property
    def gitignore_path(self) -> Path:
        """Get .gitignore path."""
        return Path.joinpath(self.project_path, ".gitignore")

    @property
    def dockerfile_path(self) -> Path:
        """Get Dockerfile path."""
        return Path.joinpath(self.project_path, "Dockerfile")

    @property
    def static_path(self) -> Path:
        """Get static directory path."""
        return Path.joinpath(self.project_path, "static")

    @property
    def css_path(self) -> Path:
        """Get CSS directory path."""
        return Path.joinpath(self.static_path, "css")

    @property
    def js_path(self) -> Path:
        """Get JavaScript directory path."""
        return Path.joinpath(self.static_path, "js")

    def get_model_path(self, app_name: str) -> Path:
        """Get models.py path for a given application."""
        return Path.joinpath(self.project_path, app_name, "models.py")

    def get_admin_path(self, app_name: str) -> Path:
        """Get admin.py path for a given application."""
        return Path.joinpath(self.project_path, app_name, "admin.py")

    # Template Operations (delegated to TemplateManager)
    def copy_templates(
        self,
        source_dir: Path,
        template_context: Optional[dict] = None,
        exclude_files: Optional[List[Path]] = None,
    ) -> None:
        """Copy template files to Django project with Jinja2 processing."""
        self._template_manager.copy_templates(
            source_dir=source_dir,
            dest_dir=self.project_path,
            template_context=template_context or {},
            exclude_files=exclude_files,
        )

    def copy_template(
        self, source_file: Path, dest_dir: Path, template_context: Optional[dict] = None
    ) -> Path:
        """Copy single template file with Jinja2 processing."""
        return self._template_manager.copy_template(
            source_file=source_file,
            dest_dir=dest_dir,
            template_context=template_context or {},
        )

    # Django Environment Management
    def add_env_variable(
        self, key: str, value: str, file_path: Optional[Path] = None
    ) -> None:
        """Add Django environment variable."""
        if file_path is None:
            file_path = self._config.devcontainer_env_devcontainer_path
        self.remove_env_variable(key, file_path)
        with open(file_path, "a") as f:
            f.write(f"{key}={value}\n")

    def remove_env_variable(self, key: str, file_path: Optional[Path] = None) -> None:
        """Remove Django environment variable."""
        if file_path is None:
            file_path = self._config.devcontainer_env_devcontainer_path
        self._template_manager.remove_lines_from_file(file_path, [f"{key}="])

    # Django Model Operations
    def get_models(self, app_name: str):
        """Parse models.py file and extract model information."""
        models_file = self.get_model_path(app_name)

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

    # Dependency Management
    def get_dependencies(self, group: str = "") -> list[str]:
        """Get list of dependencies from pyproject.toml."""
        with open(self.pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        if group:
            return pyproject_data.get("dependency-groups", {}).get(group, [])

        return pyproject_data.get("project", {}).get("dependencies", [])

    def has_dependency(self, dependency_name: str, group: str = "") -> bool:
        """Check if a specific dependency is installed."""
        dependencies = self.get_dependencies(group)
        for dep in dependencies:
            name_without_version = (
                dep.split(">")[0]
                .split("<")[0]
                .split("=")[0]
                .split("!")[0]
                .split("~")[0]
                .strip()
            )

            name_without_extras = name_without_version.split("[")[0].strip()

            if name_without_extras == dependency_name:
                return True
        return False


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
