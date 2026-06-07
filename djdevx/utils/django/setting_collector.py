"""
SettingCollector — discovers secrets and config vars from a generated Django project.

Scans all three settings directories:
  settings/django/    — core Django (SECRET_KEY, DEBUG, ALLOWED_HOSTS, …)
  settings/packages/  — installed packages (postgres password, OIDC key, …)
  settings/apps/      — user apps (any SecretStr fields the developer added)

Uses Python's ast module to extract field information from AppBaseSettings
subclasses without importing or executing the project's code.

Secrets   = fields annotated as SecretStr (or Optional[SecretStr])
Config vars = all other annotated fields (str, int, bool, list, …)

Dev defaults are extracted from the get_dev_defaults() method body, which is
always a plain dict literal in this codebase and is therefore safe to evaluate
with ast.literal_eval without executing any code.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass
class SecretInfo:
    """A secret field discovered from a settings file."""

    name: str
    source_file: Path
    generator: Optional[Callable[[], str]] = None
    dev_default: Any = None
    prod_default: Any = None

    @property
    def auto_generatable(self) -> bool:
        return self.generator is not None

    @property
    def has_dev_default(self) -> bool:
        return self.dev_default is not None


@dataclass
class ConfigVarInfo:
    """A non-secret config field discovered from a settings file."""

    name: str
    source_file: Path
    type_annotation: str = "str"
    dev_default: Any = None
    prod_default: Any = None


@dataclass
class CollectedSettings:
    """Aggregated result from SettingCollector."""

    secrets: list[SecretInfo] = field(default_factory=list)
    config_vars: list[ConfigVarInfo] = field(default_factory=list)


def _is_secret_str(annotation: ast.expr) -> bool:
    """
    Return True if the annotation is SecretStr or Optional[SecretStr].

    Handles:
      field: SecretStr
      field: Optional[SecretStr]
      field: Union[SecretStr, None]
      field: SecretStr | None
      field: str | None        (not SecretStr, so False)
    """
    if isinstance(annotation, ast.Name):
        return annotation.id == "SecretStr"
    if isinstance(annotation, ast.Subscript):
        value_id = None
        if isinstance(annotation.value, ast.Name):
            value_id = annotation.value.id
        if value_id == "Optional":
            return _is_secret_str(annotation.slice)
        if value_id == "Union":
            if isinstance(annotation.slice, ast.Tuple):
                return any(_is_secret_str(el) for el in annotation.slice.elts)
            return _is_secret_str(annotation.slice)
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        return _is_secret_str(annotation.left) or _is_secret_str(annotation.right)
    return False


def _extract_defaults(class_node: ast.ClassDef, method_name: str) -> dict[str, Any]:
    """Extract the return value of a defaults classmethod from the class AST."""
    for node in class_node.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name != method_name:
            continue
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return) and stmt.value is not None:
                try:
                    return ast.literal_eval(stmt.value)
                except (ValueError, TypeError):
                    pass
    return {}


def _extract_dev_defaults(class_node: ast.ClassDef) -> dict[str, Any]:
    return _extract_defaults(class_node, "get_dev_defaults")


def _extract_prod_defaults(class_node: ast.ClassDef) -> dict[str, Any]:
    return _extract_defaults(class_node, "get_prod_defaults")


def _annotation_to_str(annotation: ast.expr) -> str:
    """Convert an AST annotation node to its string representation."""
    return ast.unparse(annotation)


def _extract_class_default(annotation_node: ast.AnnAssign) -> Any:
    """Extract the class-level default value from an annotated assignment node.

    Handles:
      field: str = "value"                → "value"
      field: int = 42                     → 42
      field: SecretStr                    → None  (no default)
      field: SecretStr = SecretStr("")    → ""  (pydantic call default)
      field: str = Field(default="foo")   → "foo"
    """
    if annotation_node.value is None:
        return None

    # pydantic call defaults: SecretStr("val"), Field(default="val"), Field("val")
    if isinstance(annotation_node.value, ast.Call):
        func_name = None
        if isinstance(annotation_node.value.func, ast.Name):
            func_name = annotation_node.value.func.id
        if func_name in ("SecretStr", "Field"):
            if annotation_node.value.args:
                try:
                    return ast.literal_eval(annotation_node.value.args[0])
                except (ValueError, TypeError, SyntaxError):
                    pass
            for kw in annotation_node.value.keywords:
                if kw.arg == "default" and kw.value is not None:
                    try:
                        return ast.literal_eval(kw.value)
                    except (ValueError, TypeError, SyntaxError):
                        pass
            return ""
    try:
        return ast.literal_eval(annotation_node.value)
    except (ValueError, TypeError, SyntaxError):
        return None


def _parse_settings_file(
    filepath: Path,
) -> tuple[list[tuple[str, Any, Any, Any]], list[tuple[str, str, Any, Any, Any]]]:
    """Parse a single settings file via AST."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (OSError, SyntaxError):
        return [], []

    secret_fields: list[tuple[str, Any, Any, Any]] = []
    config_vars: list[tuple[str, str, Any, Any, Any]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        base_names = set()
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_names.add(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.add(base.attr)

        if "AppBaseSettings" not in base_names:
            continue

        dev_defaults = _extract_dev_defaults(node)
        prod_defaults = _extract_prod_defaults(node)

        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            if not isinstance(item.target, ast.Name):
                continue

            fname = item.target.id
            if fname.startswith("_") or fname == "model_config":
                continue

            class_default = _extract_class_default(item)

            if _is_secret_str(item.annotation):
                secret_fields.append(
                    (
                        fname,
                        dev_defaults.get(fname),
                        prod_defaults.get(fname),
                        class_default,
                    )
                )
            else:
                annotation_str = _annotation_to_str(item.annotation)
                config_vars.append(
                    (
                        fname,
                        annotation_str,
                        dev_defaults.get(fname),
                        prod_defaults.get(fname),
                        class_default,
                    )
                )

    return secret_fields, config_vars


class SettingCollector:
    """
    Discovers all secrets and config vars in a generated Django project by
    AST-parsing the settings files. Merges in generator callables from the
    djdevx package registry.
    """

    _SETTINGS_SUBDIRS = ("django", "packages", "apps")

    def __init__(self, project_path: Path) -> None:
        self._project_path = project_path
        self._settings_root = project_path / "settings"
        self._generators_index: Optional[dict[str, Callable[[], str]]] = None

    def collect(self) -> CollectedSettings:
        """Scan all settings files and return a CollectedSettings dataclass."""
        generators = self._build_generators_index()
        result = CollectedSettings()
        seen_secrets: set[str] = set()
        seen_configs: set[str] = set()

        for settings_file in self._iter_settings_files():
            secret_fields, config_vars_raw = _parse_settings_file(settings_file)

            for name, dev_default, prod_default, class_default in secret_fields:
                if name in seen_secrets:
                    continue
                seen_secrets.add(name)
                result.secrets.append(
                    SecretInfo(
                        name=name,
                        source_file=settings_file,
                        generator=generators.get(name),
                        dev_default=dev_default,
                        prod_default=prod_default or class_default,
                    )
                )

            for (
                name,
                annotation_str,
                dev_default,
                prod_default,
                class_default,
            ) in config_vars_raw:
                if name in seen_configs:
                    continue
                seen_configs.add(name)
                result.config_vars.append(
                    ConfigVarInfo(
                        name=name,
                        source_file=settings_file,
                        type_annotation=annotation_str,
                        dev_default=dev_default,
                        prod_default=prod_default or class_default,
                    )
                )

        return result

    def _iter_settings_files(self):
        """Yield all .py files from the three settings subdirectories."""
        for subdir in self._SETTINGS_SUBDIRS:
            d = self._settings_root / subdir
            if not d.exists():
                continue
            for f in sorted(d.rglob("*.py")):
                if f.name == "__init__.py":
                    continue
                yield f

    def _build_generators_index(self) -> dict[str, Callable[[], str]]:
        """Build a flat mapping of {field_name: generator} from all registered
        BasePackage subclasses, database/cache plugins, and core Django secrets."""
        if self._generators_index is not None:
            return self._generators_index

        index: dict[str, Callable[[], str]] = {}

        try:
            from djdevx.backend.django.packages._base import BasePackage

            for pkg_class in BasePackage._generator_packages:
                index.update(pkg_class.secret_generators)
        except ImportError:
            pass

        try:
            from djdevx.backend.django.packages._registries import (
                DATABASE_REGISTRY,
                CACHE_REGISTRY,
            )

            for pkg_class in DATABASE_REGISTRY.values():
                index.update(pkg_class.secret_generators)
            for pkg_class in CACHE_REGISTRY.values():
                index.update(pkg_class.secret_generators)
        except ImportError:
            pass

        # Core Django secrets — always present in every generated project.
        from djdevx.utils.generators import generate_random_password

        index["secret_key"] = lambda: generate_random_password(length=64)

        self._generators_index = index
        return index
