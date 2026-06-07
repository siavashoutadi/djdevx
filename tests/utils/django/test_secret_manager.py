"""Unit tests for SecretManager."""

import stat
from pathlib import Path

from djdevx.utils.django.secret_manager import SecretManager


class TestSecretManager:
    """Tests for SecretManager."""

    # ── write_secret ────────────────────────────────────────────────────────

    def test_write_secret_creates_file(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        mgr.write_secret("my_key", "my_value")
        assert (tmp_path / ".secrets" / "my_key").exists()

    def test_write_secret_content(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        mgr.write_secret("my_key", "my_value")
        content = (tmp_path / ".secrets" / "my_key").read_text()
        assert content == "my_value"

    def test_write_secret_file_permissions(self, tmp_path: Path) -> None:
        """Written secret file should be owner-read/write only (0o600)."""
        mgr = SecretManager(tmp_path)
        mgr.write_secret("my_key", "sensitive")
        secret_path = tmp_path / ".secrets" / "my_key"
        mode = secret_path.stat().st_mode
        # Should only have S_IRUSR | S_IWUSR (0o600)
        assert mode & 0o777 == stat.S_IRUSR | stat.S_IWUSR

    def test_write_secret_dir_permissions(self, tmp_path: Path) -> None:
        """The .secrets/ directory should be owner-only (0o700)."""
        mgr = SecretManager(tmp_path)
        mgr.write_secret("my_key", "sensitive")
        secrets_dir = tmp_path / ".secrets"
        mode = secrets_dir.stat().st_mode
        # Should only have owner rwx
        assert mode & 0o777 == stat.S_IRWXU

    def test_write_secret_creates_parent_dir(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        assert not (tmp_path / ".secrets").exists()
        mgr.write_secret("my_key", "value")
        assert (tmp_path / ".secrets").is_dir()

    def test_write_secret_overwrites_existing(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        mgr.write_secret("my_key", "first")
        mgr.write_secret("my_key", "second")
        content = (tmp_path / ".secrets" / "my_key").read_text()
        assert content == "second"

    def test_write_secret_custom_dir(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path, ".secrets.prod")
        mgr.write_secret("my_key", "prod_value")
        assert (tmp_path / ".secrets.prod" / "my_key").exists()
        assert not (tmp_path / ".secrets" / "my_key").exists()

    def test_write_multiple_secrets(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        mgr.write_secret("key1", "value1")
        mgr.write_secret("key2", "value2")
        secrets_dir = tmp_path / ".secrets"
        assert sorted(p.name for p in secrets_dir.iterdir()) == ["key1", "key2"]

    # ── has_secret ─────────────────────────────────────────────────────────

    def test_has_secret_returns_true_when_exists(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        mgr.write_secret("my_key", "value")
        assert mgr.has_secret("my_key") is True

    def test_has_secret_returns_false_when_missing(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        assert mgr.has_secret("nonexistent") is False

    def test_has_secret_returns_false_before_write(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        assert mgr.has_secret("my_key") is False
        mgr.write_secret("my_key", "value")
        assert mgr.has_secret("my_key") is True

    def test_has_secret_custom_dir(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path, ".secrets.prod")
        assert mgr.has_secret("my_key") is False
        mgr.write_secret("my_key", "value")
        assert mgr.has_secret("my_key") is True

    # ── remove_secret ──────────────────────────────────────────────────────

    def test_remove_secret_deletes_file(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        mgr.write_secret("my_key", "value")
        mgr.remove_secret("my_key")
        assert not (tmp_path / ".secrets" / "my_key").exists()

    def test_remove_secret_missing_is_noop(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        mgr.remove_secret("nonexistent")
        assert True  # No exception raised

    def test_remove_secret_then_has_returns_false(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path)
        mgr.write_secret("my_key", "value")
        assert mgr.has_secret("my_key") is True
        mgr.remove_secret("my_key")
        assert mgr.has_secret("my_key") is False

    def test_remove_secret_custom_dir(self, tmp_path: Path) -> None:
        mgr = SecretManager(tmp_path, ".secrets.prod")
        mgr.write_secret("my_key", "value")
        mgr.remove_secret("my_key")
        assert not (tmp_path / ".secrets.prod" / "my_key").exists()

    # ── constructor ────────────────────────────────────────────────────────

    def test_default_dir_name(self) -> None:
        mgr = SecretManager(Path("/tmp"))
        assert mgr._secrets_dir == Path("/tmp") / ".secrets"

    def test_custom_dir_name(self) -> None:
        mgr = SecretManager(Path("/tmp"), ".custom-secrets")
        assert mgr._secrets_dir == Path("/tmp") / ".custom-secrets"
