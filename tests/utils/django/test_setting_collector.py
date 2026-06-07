"""Unit tests for SettingCollector."""

import ast
from pathlib import Path

from djdevx.utils.django.setting_collector import (
    _extract_class_default,
    _extract_defaults,
    _is_secret_str,
    _parse_settings_file,
    SecretInfo,
    ConfigVarInfo,
    SettingCollector,
    CollectedSettings,
)


# ── _is_secret_str ─────────────────────────────────────────────────────────────


class TestIsSecretStr:
    """Tests for _is_secret_str AST annotation detection."""

    def _parse_annotation(self, code: str) -> ast.expr:
        tree = ast.parse(code)
        return tree.body[0].annotation  # type: ignore[attr-defined]

    def test_secret_str(self) -> None:
        ann = self._parse_annotation("x: SecretStr")
        assert _is_secret_str(ann) is True

    def test_str_is_not_secret(self) -> None:
        ann = self._parse_annotation("x: str")
        assert _is_secret_str(ann) is False

    def test_int_is_not_secret(self) -> None:
        ann = self._parse_annotation("x: int")
        assert _is_secret_str(ann) is False

    def test_bool_is_not_secret(self) -> None:
        ann = self._parse_annotation("x: bool")
        assert _is_secret_str(ann) is False

    def test_list_is_not_secret(self) -> None:
        ann = self._parse_annotation("x: list[str]")
        assert _is_secret_str(ann) is False

    def test_optional_secret_str(self) -> None:
        ann = self._parse_annotation("x: Optional[SecretStr]")
        assert _is_secret_str(ann) is True

    def test_optional_str_is_not_secret(self) -> None:
        ann = self._parse_annotation("x: Optional[str]")
        assert _is_secret_str(ann) is False

    def test_union_secret_str_none(self) -> None:
        ann = self._parse_annotation("x: Union[SecretStr, None]")
        assert _is_secret_str(ann) is True

    def test_union_str_none_is_not_secret(self) -> None:
        ann = self._parse_annotation("x: Union[str, None]")
        assert _is_secret_str(ann) is False

    def test_pep604_secret_str_none(self) -> None:
        ann = self._parse_annotation("x: SecretStr | None")
        assert _is_secret_str(ann) is True

    def test_pep604_str_none_is_not_secret(self) -> None:
        ann = self._parse_annotation("x: str | None")
        assert _is_secret_str(ann) is False

    def test_pep604_complex_not_secret(self) -> None:
        ann = self._parse_annotation("x: int | str")
        assert _is_secret_str(ann) is False

    def test_none_annotation(self) -> None:
        """No annotation (ellipsis / missing) should not crash."""
        # This tests the function with a non-annotation node
        assert _is_secret_str(ast.Constant(value=None)) is False


# ── _extract_class_default ─────────────────────────────────────────────────────


class TestExtractClassDefault:
    """Tests for _extract_class_default AST extraction."""

    def _parse_assign(self, code: str) -> ast.AnnAssign:
        tree = ast.parse(code)
        return tree.body[0]  # type: ignore[return-value]

    def test_str_default(self) -> None:
        node = self._parse_assign("x: str = 'hello'")
        assert _extract_class_default(node) == "hello"

    def test_int_default(self) -> None:
        node = self._parse_assign("x: int = 42")
        assert _extract_class_default(node) == 42

    def test_bool_default(self) -> None:
        node = self._parse_assign("x: bool = True")
        assert _extract_class_default(node) is True

    def test_list_default(self) -> None:
        node = self._parse_assign("x: list = []")
        assert _extract_class_default(node) == []

    def test_no_default(self) -> None:
        node = self._parse_assign("x: str")
        assert _extract_class_default(node) is None

    def test_secret_str_no_default(self) -> None:
        node = self._parse_assign("x: SecretStr")
        assert _extract_class_default(node) is None

    def test_secret_str_with_empty_call(self) -> None:
        """SecretStr("") — function call default."""
        node = self._parse_assign("x: SecretStr = SecretStr('')")
        assert _extract_class_default(node) == ""

    def test_secret_str_with_value_call(self) -> None:
        """SecretStr("s3cret") — function call default."""
        node = self._parse_assign("x: SecretStr = SecretStr('s3cret')")
        assert _extract_class_default(node) == "s3cret"

    def test_field_call_with_default(self) -> None:
        """Field(default=...) call default."""
        node = self._parse_assign("x: str = Field(default='foo')")
        assert _extract_class_default(node) == "foo"

    def test_complex_expression_default(self) -> None:
        """Defaults that are complex expressions should not crash."""
        node = self._parse_assign("x: int = some_func()")
        result = _extract_class_default(node)
        # Should gracefully return None for non-literal expressions
        assert result is None


# ── _extract_defaults ──────────────────────────────────────────────────────────


class TestExtractDefaults:
    """Tests for _extract_defaults AST extraction from classmethods."""

    def test_extract_dev_defaults(self) -> None:
        code = """
class MySettings(AppBaseSettings):
    @classmethod
    def get_dev_defaults(cls) -> dict:
        return {"key": "value", "num": 42}
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)
        result = _extract_defaults(class_node, "get_dev_defaults")
        assert result == {"key": "value", "num": 42}

    def test_extract_empty_defaults(self) -> None:
        code = """
class MySettings(AppBaseSettings):
    @classmethod
    def get_dev_defaults(cls) -> dict:
        return {}
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)
        result = _extract_defaults(class_node, "get_dev_defaults")
        assert result == {}

    def test_extract_no_method_returns_empty(self) -> None:
        code = """
class MySettings(AppBaseSettings):
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)
        result = _extract_defaults(class_node, "get_dev_defaults")
        assert result == {}

    def test_extract_prod_defaults(self) -> None:
        code = """
class MySettings(AppBaseSettings):
    @classmethod
    def get_prod_defaults(cls) -> dict:
        return {"key": "prod_value"}
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert isinstance(class_node, ast.ClassDef)
        result = _extract_defaults(class_node, "get_prod_defaults")
        assert result == {"key": "prod_value"}


# ── _parse_settings_file ───────────────────────────────────────────────────────


class TestParseSettingsFile:
    """Tests for _parse_settings_file."""

    def test_parse_secret_and_config(self, tmp_path: Path) -> None:
        file = tmp_path / "settings.py"
        file.write_text("""
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings

class MySettings(AppBaseSettings):
    secret_key: SecretStr
    debug: bool = True
    allowed_hosts: list[str] = ["localhost"]

    @classmethod
    def get_dev_defaults(cls) -> dict:
        return {"debug": True, "allowed_hosts": ["127.0.0.1"]}
""")
        secrets, configs = _parse_settings_file(file)
        assert len(secrets) == 1
        assert secrets[0][0] == "secret_key"
        assert len(configs) == 2
        config_names = {c[0] for c in configs}
        assert config_names == {"debug", "allowed_hosts"}

    def test_skip_private_and_model_config(self, tmp_path: Path) -> None:
        file = tmp_path / "settings.py"
        file.write_text("""
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings

class MySettings(AppBaseSettings):
    _private_field: str = "hidden"
    model_config: dict = {}
    public_field: str = "visible"
""")
        secrets, configs = _parse_settings_file(file)
        assert len(secrets) == 0
        config_names = {c[0] for c in configs}
        assert config_names == {"public_field"}

    def test_skip_non_appbase_settings(self, tmp_path: Path) -> None:
        file = tmp_path / "settings.py"
        file.write_text("""
class OtherSettings:
    secret_key: str = "nope"
""")
        secrets, configs = _parse_settings_file(file)
        assert len(secrets) == 0
        assert len(configs) == 0

    def test_syntax_error_returns_empty(self, tmp_path: Path) -> None:
        file = tmp_path / "settings.py"
        file.write_text("this is not valid python {{{")
        secrets, configs = _parse_settings_file(file)
        assert secrets == []
        assert configs == []


# ── SettingCollector ───────────────────────────────────────────────────────────


class TestSettingCollector:
    """Tests for SettingCollector."""

    def _make_settings_file(self, base: Path, *parts: str, content: str) -> Path:
        """Create a settings file under base/settings/subdir/name.py."""
        subdir = (
            base / "settings" / parts[0]
            if len(parts) == 1
            else base / "settings" / parts[0] / parts[1]
        )
        subdir.mkdir(parents=True, exist_ok=True)
        file_path = subdir / f"{parts[-1]}.py"
        file_path.write_text(content)
        return file_path

    def test_collects_secrets_from_django_dir(self, tmp_path: Path) -> None:
        self._make_settings_file(
            tmp_path,
            "django",
            "base",
            content="""
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings

class MySettings(AppBaseSettings):
    secret_key: SecretStr
    debug: bool = True
""",
        )
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        assert len(result.secrets) == 1
        assert result.secrets[0].name == "secret_key"
        assert len(result.config_vars) == 1
        assert result.config_vars[0].name == "debug"

    def test_collects_from_multiple_dirs(self, tmp_path: Path) -> None:
        self._make_settings_file(
            tmp_path,
            "django",
            "base",
            content="""
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings

class DjangoCfg(AppBaseSettings):
    secret_key: SecretStr
""",
        )
        self._make_settings_file(
            tmp_path,
            "packages",
            "postgres",
            content="""
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings

class DBSettings(AppBaseSettings):
    db_password: SecretStr
    db_host: str = "localhost"
""",
        )
        self._make_settings_file(
            tmp_path,
            "apps",
            "myapp",
            content="""
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings

class AppCfg(AppBaseSettings):
    app_token: SecretStr
""",
        )
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        secret_names = {s.name for s in result.secrets}
        assert secret_names == {"secret_key", "db_password", "app_token"}
        config_names = {c.name for c in result.config_vars}
        assert config_names == {"db_host"}

    def test_skips_init_py(self, tmp_path: Path) -> None:
        self._make_settings_file(
            tmp_path,
            "django",
            "__init__",
            content="""
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings

class InitSettings(AppBaseSettings):
    should_skip: SecretStr
""",
        )
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        assert len(result.secrets) == 0

    def test_deduplicates_same_name(self, tmp_path: Path) -> None:
        """Same-named field across two files should appear only once (first wins)."""
        self._make_settings_file(
            tmp_path,
            "django",
            "base",
            content="""
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings

class Cfg1(AppBaseSettings):
    shared_field: str = "from_base"
""",
        )
        self._make_settings_file(
            tmp_path,
            "packages",
            "extra",
            content="""
from settings.utils.base_settings import AppBaseSettings

class Cfg2(AppBaseSettings):
    shared_field: str = "from_extra"
""",
        )
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        assert len(result.config_vars) == 1
        assert result.config_vars[0].name == "shared_field"
        # prod_default falls back to class default from first file
        assert result.config_vars[0].prod_default == "from_base"

    def test_extracts_dev_defaults(self, tmp_path: Path) -> None:
        self._make_settings_file(
            tmp_path,
            "django",
            "base",
            content="""
from typing import Any
from settings.utils.base_settings import AppBaseSettings

class MySettings(AppBaseSettings):
    debug: bool
    allowed_hosts: list[str]

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"debug": True, "allowed_hosts": ["localhost"]}
""",
        )
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        cfg = {c.name: c for c in result.config_vars}
        assert cfg["debug"].dev_default is True
        assert cfg["allowed_hosts"].dev_default == ["localhost"]

    def test_dev_default_overrides_class_default(self, tmp_path: Path) -> None:
        """get_dev_defaults should take precedence over class-level defaults."""
        self._make_settings_file(
            tmp_path,
            "django",
            "base",
            content="""
from typing import Any
from settings.utils.base_settings import AppBaseSettings

class MySettings(AppBaseSettings):
    debug: bool = False

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"debug": True}
""",
        )
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        assert result.config_vars[0].dev_default is True

    def test_missing_settings_dir_returns_empty(self, tmp_path: Path) -> None:
        """No settings/ directory at all."""
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        assert len(result.secrets) == 0
        assert len(result.config_vars) == 0

    def test_empty_settings_dirs_return_empty(self, tmp_path: Path) -> None:
        """Empty settings/ directories."""
        (tmp_path / "settings" / "django").mkdir(parents=True)
        (tmp_path / "settings" / "packages").mkdir(parents=True)
        (tmp_path / "settings" / "apps").mkdir(parents=True)
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        assert len(result.secrets) == 0
        assert len(result.config_vars) == 0

    def test_prod_default_falls_back_to_class_default(self, tmp_path: Path) -> None:
        self._make_settings_file(
            tmp_path,
            "django",
            "base",
            content="""
from settings.utils.base_settings import AppBaseSettings

class MySettings(AppBaseSettings):
    debug: bool = False
""",
        )
        collector = SettingCollector(tmp_path)
        result = collector.collect()
        assert result.config_vars[0].prod_default is False

    def test_collected_settings_dataclass(self) -> None:
        """CollectedSettings dataclass works as expected."""
        cs = CollectedSettings(
            secrets=[SecretInfo(name="sec1", source_file=Path("x.py"))],
            config_vars=[ConfigVarInfo(name="cfg1", source_file=Path("y.py"))],
        )
        assert len(cs.secrets) == 1
        assert len(cs.config_vars) == 1

    def test_secret_info_has_dev_default(self) -> None:
        si = SecretInfo(name="x", source_file=Path("x.py"), dev_default=None)
        assert si.has_dev_default is False
        si2 = SecretInfo(name="y", source_file=Path("y.py"), dev_default="val")
        assert si2.has_dev_default is True

    def test_secret_info_auto_generatable(self) -> None:
        si = SecretInfo(name="x", source_file=Path("x.py"))
        assert si.auto_generatable is False
        si2 = SecretInfo(name="y", source_file=Path("y.py"), generator=lambda: "val")
        assert si2.auto_generatable is True
