"""Unit tests for _source.py resolution functions."""

import os
from pathlib import Path

import pytest

from dotenv import set_key

from djdevx.backend.django.settings._source import (
    ConfigSource,
    SecretSource,
    read_env_file,
    read_dot_env,
    read_env_prod,
    resolve_config_source_dev,
    resolve_config_source_prod,
    resolve_config_value_dev,
    resolve_config_value_prod,
    resolve_secret_source_dev,
    resolve_secret_source_prod,
)
from djdevx.utils.django.setting_collector import ConfigVarInfo, SecretInfo


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def backend_root(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def config_var() -> ConfigVarInfo:
    return ConfigVarInfo(
        name="test_var",
        source_file=Path("dummy.py"),
        type_annotation="str",
        dev_default="dev_fallback",
        prod_default="prod_fallback",
    )


@pytest.fixture
def secret_info() -> SecretInfo:
    return SecretInfo(
        name="test_secret",
        source_file=Path("dummy.py"),
        dev_default="dev_secret",
    )


# ── read_env_file ──────────────────────────────────────────────────────────────


class TestReadEnvFile:
    def test_reads_key_value(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("KEY=value\nOTHER=thing")
        result = read_env_file(f)
        assert result == {"KEY": "value", "OTHER": "thing"}

    def test_skips_comments(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("# comment\nKEY=value")
        result = read_env_file(f)
        assert result == {"KEY": "value"}

    def test_skips_empty_lines(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("KEY=value\n\nOTHER=thing")
        result = read_env_file(f)
        assert result == {"KEY": "value", "OTHER": "thing"}

    def test_missing_file_returns_empty(self) -> None:
        result = read_env_file(Path("/nonexistent/.env"))
        assert result == {}

    def test_strips_whitespace(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("  KEY  =  value  ")
        result = read_env_file(f)
        assert result == {"KEY": "value"}


# ── read_dot_env / read_env_prod ───────────────────────────────────────────────


class TestReadDotEnv:
    def test_reads_dot_env(self, tmp_path: Path) -> None:
        set_key(tmp_path / ".env", "KEY", "value")
        result = read_dot_env(tmp_path)
        assert result == {"KEY": "value"}

    def test_missing_dot_env(self, tmp_path: Path) -> None:
        result = read_dot_env(tmp_path)
        assert result == {}


class TestReadEnvProd:
    def test_reads_env_prod(self, tmp_path: Path) -> None:
        set_key(tmp_path / ".env.prod", "KEY", "prod_value")
        result = read_env_prod(tmp_path)
        assert result == {"KEY": "prod_value"}

    def test_missing_env_prod(self, tmp_path: Path) -> None:
        result = read_env_prod(tmp_path)
        assert result == {}


# ── resolve_config_source_dev ──────────────────────────────────────────────────


class TestResolveConfigSourceDev:
    def test_os_environ_wins(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        os.environ["TEST_VAR"] = "from_env"
        try:
            src = resolve_config_source_dev(config_var, backend_root)
            assert src == ConfigSource.OS_ENVIRON
        finally:
            del os.environ["TEST_VAR"]

    def test_dot_env_fallback(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        set_key(backend_root / ".env", "TEST_VAR", "from_dotenv")
        src = resolve_config_source_dev(config_var, backend_root)
        assert src == ConfigSource.DOT_ENV

    def test_dev_default_fallback(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        src = resolve_config_source_dev(config_var, backend_root)
        assert src == ConfigSource.DEV_DEFAULT

    def test_missing_when_no_dev_default(self, backend_root: Path) -> None:
        config_var = ConfigVarInfo(
            name="required", source_file=Path("x.py"), dev_default=None
        )
        src = resolve_config_source_dev(config_var, backend_root)
        assert src == ConfigSource.MISSING

    def test_os_environ_overrides_dot_env(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        set_key(backend_root / ".env", "TEST_VAR", "from_dotenv")
        os.environ["TEST_VAR"] = "from_env"
        try:
            src = resolve_config_source_dev(config_var, backend_root)
            assert src == ConfigSource.OS_ENVIRON
        finally:
            del os.environ["TEST_VAR"]


# ── resolve_config_source_prod ─────────────────────────────────────────────────


class TestResolveConfigSourceProd:
    def test_os_environ_wins(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        os.environ["TEST_VAR"] = "from_env"
        try:
            src = resolve_config_source_prod(config_var, backend_root)
            assert src == ConfigSource.OS_ENVIRON
        finally:
            del os.environ["TEST_VAR"]

    def test_env_prod_fallback(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        set_key(backend_root / ".env.prod", "TEST_VAR", "from_envprod")
        src = resolve_config_source_prod(config_var, backend_root)
        assert src == ConfigSource.ENV_PROD

    def test_prod_default_fallback(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        src = resolve_config_source_prod(config_var, backend_root)
        assert src == ConfigSource.PROD_DEFAULT

    def test_missing_when_no_prod_default(self, backend_root: Path) -> None:
        config_var = ConfigVarInfo(
            name="required", source_file=Path("x.py"), prod_default=None
        )
        src = resolve_config_source_prod(config_var, backend_root)
        assert src == ConfigSource.MISSING

    def test_os_environ_overrides_env_prod(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        set_key(backend_root / ".env.prod", "TEST_VAR", "from_envprod")
        os.environ["TEST_VAR"] = "from_env"
        try:
            src = resolve_config_source_prod(config_var, backend_root)
            assert src == ConfigSource.OS_ENVIRON
        finally:
            del os.environ["TEST_VAR"]


# ── resolve_config_value_dev ───────────────────────────────────────────────────


class TestResolveConfigValueDev:
    def test_returns_env_value(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        os.environ["TEST_VAR"] = "env_value"
        try:
            val = resolve_config_value_dev(config_var, backend_root)
            assert val == "env_value"
        finally:
            del os.environ["TEST_VAR"]

    def test_returns_dot_env_value(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        set_key(backend_root / ".env", "TEST_VAR", "dotenv_value")
        val = resolve_config_value_dev(config_var, backend_root)
        assert val == "dotenv_value"

    def test_returns_dev_default(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        val = resolve_config_value_dev(config_var, backend_root)
        assert val == "dev_fallback"

    def test_returns_none_when_missing(self, backend_root: Path) -> None:
        config_var = ConfigVarInfo(
            name="missing", source_file=Path("x.py"), dev_default=None
        )
        val = resolve_config_value_dev(config_var, backend_root)
        assert val is None


# ── resolve_config_value_prod ──────────────────────────────────────────────────


class TestResolveConfigValueProd:
    def test_returns_env_value(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        os.environ["TEST_VAR"] = "env_value"
        try:
            val = resolve_config_value_prod(config_var, backend_root)
            assert val == "env_value"
        finally:
            del os.environ["TEST_VAR"]

    def test_returns_env_prod_value(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        set_key(backend_root / ".env.prod", "TEST_VAR", "prod_value")
        val = resolve_config_value_prod(config_var, backend_root)
        assert val == "prod_value"

    def test_returns_prod_default(
        self, backend_root: Path, config_var: ConfigVarInfo
    ) -> None:
        val = resolve_config_value_prod(config_var, backend_root)
        assert val == "prod_fallback"

    def test_returns_none_when_missing(self, backend_root: Path) -> None:
        config_var = ConfigVarInfo(
            name="missing", source_file=Path("x.py"), prod_default=None
        )
        val = resolve_config_value_prod(config_var, backend_root)
        assert val is None


# ── resolve_secret_source_dev ──────────────────────────────────────────────────


class TestResolveSecretSourceDev:
    def test_secrets_dir_found(
        self, backend_root: Path, secret_info: SecretInfo
    ) -> None:
        (backend_root / ".secrets").mkdir()
        (backend_root / ".secrets" / "test_secret").write_text("sensitive")
        src = resolve_secret_source_dev(secret_info, backend_root)
        assert src == ".secrets/test_secret"

    def test_dev_default_fallback(
        self, backend_root: Path, secret_info: SecretInfo
    ) -> None:
        src = resolve_secret_source_dev(secret_info, backend_root)
        assert src == SecretSource.DEV_DEFAULT

    def test_missing_when_no_dev_default(self, backend_root: Path) -> None:
        si = SecretInfo(name="required", source_file=Path("x.py"), dev_default=None)
        src = resolve_secret_source_dev(si, backend_root)
        assert src == SecretSource.MISSING

    def test_secrets_takes_priority_over_default(
        self, backend_root: Path, secret_info: SecretInfo
    ) -> None:
        (backend_root / ".secrets").mkdir()
        (backend_root / ".secrets" / "test_secret").write_text("sensitive")
        src = resolve_secret_source_dev(secret_info, backend_root)
        assert src == ".secrets/test_secret"


# ── resolve_secret_source_prod ──────────────────────────────────────────────────


class TestResolveSecretSourceProd:
    def test_secrets_prod_found(
        self, backend_root: Path, secret_info: SecretInfo
    ) -> None:
        (backend_root / ".secrets.prod").mkdir()
        (backend_root / ".secrets.prod" / "test_secret").write_text("sensitive")
        src = resolve_secret_source_prod(secret_info, backend_root)
        assert src == ".secrets.prod/test_secret"

    def test_prod_default_fallback(self, backend_root: Path) -> None:
        si = SecretInfo(name="sec", source_file=Path("x.py"), prod_default="fallback")
        src = resolve_secret_source_prod(si, backend_root)
        assert src == SecretSource.PROD_DEFAULT

    def test_missing_when_no_prod_default(
        self, backend_root: Path, secret_info: SecretInfo
    ) -> None:
        src = resolve_secret_source_prod(secret_info, backend_root)
        assert src == SecretSource.MISSING
