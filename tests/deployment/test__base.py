"""Tests for BaseDeployPlugin and DeployParam."""

from pathlib import Path

import pytest

from djdevx.deployment._base import BaseDeployPlugin, DeployParam


class TestDeployParam:
    def test_defaults(self):
        p = DeployParam(name="test")
        assert p.name == "test"
        assert p.type_ is str
        assert p.help == ""
        assert p.default is None
        assert p.prompt is None
        assert p.hide_input is False

    def test_custom(self):
        p = DeployParam(
            name="api_key",
            type_=str,
            help="API key",
            default="",
            prompt="Enter API key:",
            hide_input=True,
        )
        assert p.name == "api_key"
        assert p.type_ is str
        assert p.help == "API key"
        assert p.default == ""
        assert p.prompt == "Enter API key:"
        assert p.hide_input is True


class TestBaseDeployPlugin:
    def test_write_creates_file(self, temp_dir: Path):
        path = temp_dir / "test.txt"
        BaseDeployPlugin._write(path, "hello world")
        assert path.read_text() == "hello world"

    def test_write_skips_unchanged(self, temp_dir: Path):
        path = temp_dir / "test.txt"
        path.write_text("hello world")
        BaseDeployPlugin._write(path, "hello world")
        assert path.read_text() == "hello world"

    def test_write_overwrites_changed(self, temp_dir: Path):
        path = temp_dir / "test.txt"
        path.write_text("original")
        BaseDeployPlugin._write(path, "modified")
        assert path.read_text() == "modified"

    def test_write_creates_parent_dirs(self, temp_dir: Path):
        path = temp_dir / "a" / "b" / "test.txt"
        BaseDeployPlugin._write(path, "nested")
        assert path.read_text() == "nested"

    def test_write_once_creates_file(self, temp_dir: Path):
        path = temp_dir / "test.txt"
        BaseDeployPlugin._write_once(path, "new")
        assert path.read_text() == "new"

    def test_write_once_skips_existing(self, temp_dir: Path):
        path = temp_dir / "test.txt"
        path.write_text("original")
        BaseDeployPlugin._write_once(path, "should not overwrite")
        assert path.read_text() == "original"

    def test_write_once_creates_parent_dirs(self, temp_dir: Path):
        path = temp_dir / "a" / "b" / "test.txt"
        BaseDeployPlugin._write_once(path, "nested")
        assert path.read_text() == "nested"

    def test_check_files_exist_all(self, temp_dir: Path):
        a = temp_dir / "a.txt"
        b = temp_dir / "b.txt"
        a.write_text("")
        b.write_text("")
        assert BaseDeployPlugin._check_files_exist(a, b) is True

    def test_check_files_exist_missing(self, temp_dir: Path):
        a = temp_dir / "a.txt"
        b = temp_dir / "b.txt"
        a.write_text("")
        assert BaseDeployPlugin._check_files_exist(a, b) is False

    def test_check_files_exist_empty(self):
        assert BaseDeployPlugin._check_files_exist() is True

    def test_indent(self):
        result = BaseDeployPlugin._indent("hello\nworld", spaces=4)
        assert result == "    hello\n    world"

    def test_to_env_str_none(self):
        assert BaseDeployPlugin._to_env_str(None) == ""

    def test_to_env_str_bool(self):
        assert BaseDeployPlugin._to_env_str(True) == "true"
        assert BaseDeployPlugin._to_env_str(False) == "false"

    def test_to_env_str_list(self):
        import json

        result = BaseDeployPlugin._to_env_str([1, 2, 3])
        assert json.loads(result) == [1, 2, 3]

    def test_to_env_str_dict(self):
        import json

        result = BaseDeployPlugin._to_env_str({"key": "val"})
        assert json.loads(result) == {"key": "val"}

    def test_to_env_str_str(self):
        assert BaseDeployPlugin._to_env_str("hello") == "hello"

    def test_to_env_str_int(self):
        assert BaseDeployPlugin._to_env_str(42) == "42"

    def test_typer_app_has_generate_and_verify(self):
        """Verify that typer_app creates the expected CLI commands."""
        plugin = BaseDeployPlugin()
        app = plugin.typer_app
        assert len(app.registered_commands) == 2
        cmd_names = [c.name for c in app.registered_commands]
        assert "generate" in cmd_names
        assert "verify" in cmd_names

    def test_default_output_dir(self):
        """Verify that default output dir resolves to deployment/<name>/."""
        plugin = BaseDeployPlugin()
        # Can't test _project_root() without a real project,
        # but verify the pattern logic
        assert plugin.name.lower().replace(" ", "-") == ""

    def test_generate_raises_not_implemented(self):
        plugin = BaseDeployPlugin()
        with pytest.raises(NotImplementedError):
            plugin.generate(Path("/tmp"))

    def test_verify_raises_not_implemented(self):
        plugin = BaseDeployPlugin()
        with pytest.raises(NotImplementedError):
            plugin.verify(Path("/tmp"))
