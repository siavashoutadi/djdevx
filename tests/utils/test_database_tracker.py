"""Unit tests for DatabaseTracker."""

from pathlib import Path

import pytest
import tomlkit

from djdevx.utils.djdevx_config.backend.database_tracker import DatabaseTracker


@pytest.fixture
def tracker(tmp_path: Path) -> DatabaseTracker:
    """
    Return a DatabaseTracker whose djdevx_root is isolated to tmp_path/.djdevx.
    Uses a local subclass to override the property without touching the real filesystem.
    """
    djdevx_root = tmp_path / ".djdevx"
    djdevx_root.mkdir(parents=True)

    class IsolatedTracker(DatabaseTracker):
        @property
        def djdevx_root(self) -> Path:  # type: ignore[override]
            return djdevx_root

    return IsolatedTracker()


# ── write_database_config ─────────────────────────────────────────────────────


class TestWriteDatabaseConfig:
    """Tests for DatabaseTracker.write_database_config."""

    def test_creates_config_toml(self, tracker: DatabaseTracker) -> None:
        """write_database_config creates the config.toml file."""
        tracker.write_database_config("postgres", "postgres")
        assert tracker._config_path("postgres").exists()

    def test_config_contains_database_section(self, tracker: DatabaseTracker) -> None:
        """config.toml contains a [database] table with the correct name."""
        tracker.write_database_config("postgres", "postgres")
        doc = tomlkit.loads(tracker._config_path("postgres").read_text()).unwrap()
        assert doc["database"]["name"] == "postgres"

    def test_creates_parent_directories(self, tracker: DatabaseTracker) -> None:
        """Intermediate directories are created automatically."""
        tracker.write_database_config("postgres", "postgres")
        assert tracker._config_path("postgres").exists()

    def test_overwrite_updates_name(self, tracker: DatabaseTracker) -> None:
        """Calling write_database_config twice updates the name in place."""
        tracker.write_database_config("postgres", "old name")
        tracker.write_database_config("postgres", "postgres")
        doc = tomlkit.loads(tracker._config_path("postgres").read_text()).unwrap()
        assert doc["database"]["name"] == "postgres"


# ── read_database_config ──────────────────────────────────────────────────────


class TestReadDatabaseConfig:
    """Tests for DatabaseTracker.read_database_config."""

    def test_reads_written_config(self, tracker: DatabaseTracker) -> None:
        """read_database_config returns the same data that was written."""
        tracker.write_database_config("postgres", "postgres")
        doc = tracker.read_database_config("postgres").unwrap()
        assert doc["database"]["name"] == "postgres"


# ── remove_database_config ────────────────────────────────────────────────────


class TestRemoveDatabaseConfig:
    """Tests for DatabaseTracker.remove_database_config."""

    def test_removes_tracking_directory(self, tracker: DatabaseTracker) -> None:
        """remove_database_config deletes the entire database tracking directory."""
        tracker.write_database_config("postgres", "postgres")
        assert tracker._database_dir("postgres").exists()
        tracker.remove_database_config("postgres")
        assert not tracker._database_dir("postgres").exists()

    def test_noop_when_not_installed(self, tracker: DatabaseTracker) -> None:
        """remove_database_config does not raise when the database was never installed."""
        tracker.remove_database_config("postgres")  # should not raise


# ── is_installed ──────────────────────────────────────────────────────────────


class TestIsInstalled:
    """Tests for DatabaseTracker.is_installed."""

    def test_returns_false_before_install(self, tracker: DatabaseTracker) -> None:
        assert tracker.is_installed("postgres") is False

    def test_returns_true_after_write(self, tracker: DatabaseTracker) -> None:
        tracker.write_database_config("postgres", "postgres")
        assert tracker.is_installed("postgres") is True

    def test_returns_false_after_remove(self, tracker: DatabaseTracker) -> None:
        tracker.write_database_config("postgres", "postgres")
        tracker.remove_database_config("postgres")
        assert tracker.is_installed("postgres") is False

    def test_unrelated_databases_are_independent(
        self, tracker: DatabaseTracker
    ) -> None:
        """Installing one database does not affect is_installed for another."""
        tracker.write_database_config("postgres", "postgres")
        assert tracker.is_installed("postgres") is True
        assert tracker.is_installed("mysql") is False


# ── path helpers ──────────────────────────────────────────────────────────────


class TestDatabaseRoot:
    """Tests for the internal path helpers."""

    def test_database_root_path(self, tracker: DatabaseTracker) -> None:
        expected = tracker.djdevx_root / "backend" / "django" / "database"
        assert tracker._database_root == expected

    def test_database_dir(self, tracker: DatabaseTracker) -> None:
        expected = tracker.djdevx_root / "backend" / "django" / "database" / "postgres"
        assert tracker._database_dir("postgres") == expected

    def test_config_path(self, tracker: DatabaseTracker) -> None:
        expected = (
            tracker.djdevx_root
            / "backend"
            / "django"
            / "database"
            / "postgres"
            / "config.toml"
        )
        assert tracker._config_path("postgres") == expected
