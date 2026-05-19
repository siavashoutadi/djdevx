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

    def test_overwrite_preserves_env_section(self, tracker: DatabaseTracker) -> None:
        """Re-writing [database] does not discard an existing [env] section."""
        tracker.write_database_config("postgres", "postgres")
        tracker.write_env_entries(
            "postgres", {"POSTGRES_DB": {"type": "user_input", "value": "postgres"}}
        )
        tracker.write_database_config("postgres", "postgres")
        doc = tomlkit.loads(tracker._config_path("postgres").read_text()).unwrap()
        assert "env" in doc, "[env] section was lost after re-writing [database]"


# ── write_env_entries ─────────────────────────────────────────────────────────


class TestWriteEnvEntries:
    """Tests for DatabaseTracker.write_env_entries."""

    def test_writes_user_input_with_value(self, tracker: DatabaseTracker) -> None:
        """user_input entries are written with their value."""
        tracker.write_database_config("postgres", "postgres")
        tracker.write_env_entries(
            "postgres",
            {
                "POSTGRES_SERVER": {"type": "user_input", "value": "db"},
            },
        )
        doc = tomlkit.loads(tracker._config_path("postgres").read_text()).unwrap()
        assert doc["env"]["POSTGRES_SERVER"]["type"] == "user_input"
        assert doc["env"]["POSTGRES_SERVER"]["value"] == "db"

    def test_writes_secret_without_value(self, tracker: DatabaseTracker) -> None:
        """Secret entries are written with type only — value is never stored."""
        tracker.write_database_config("postgres", "postgres")
        tracker.write_env_entries(
            "postgres",
            {
                "POSTGRES_PASSWORD": {"type": "secret"},
            },
        )
        doc = tomlkit.loads(tracker._config_path("postgres").read_text()).unwrap()
        assert doc["env"]["POSTGRES_PASSWORD"]["type"] == "secret"
        assert "value" not in doc["env"]["POSTGRES_PASSWORD"]

    def test_writes_all_postgres_env_vars(self, tracker: DatabaseTracker) -> None:
        """All six PostgreSQL env vars are written correctly."""
        tracker.write_database_config("postgres", "postgres")
        tracker.write_env_entries(
            "postgres",
            {
                "POSTGRES_SERVER": {"type": "user_input", "value": "db"},
                "POSTGRES_PORT": {"type": "user_input", "value": "5432"},
                "POSTGRES_USER": {"type": "user_input", "value": "postgres"},
                "POSTGRES_PASSWORD": {"type": "secret"},
                "POSTGRES_DB": {"type": "user_input", "value": "postgres"},
                "PGDATA": {
                    "type": "user_input",
                    "value": "/var/lib/postgresql/data/pgdata",
                },
            },
        )
        doc = tomlkit.loads(tracker._config_path("postgres").read_text()).unwrap()
        env = doc["env"]
        assert set(env.keys()) == {
            "POSTGRES_SERVER",
            "POSTGRES_PORT",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
            "PGDATA",
        }

    def test_env_preserves_database_section(self, tracker: DatabaseTracker) -> None:
        """Writing [env] does not discard the existing [database] section."""
        tracker.write_database_config("postgres", "postgres")
        tracker.write_env_entries(
            "postgres",
            {
                "POSTGRES_DB": {"type": "user_input", "value": "postgres"},
            },
        )
        doc = tomlkit.loads(tracker._config_path("postgres").read_text()).unwrap()
        assert doc["database"]["name"] == "postgres"

    def test_env_section_is_replaced_on_second_call(
        self, tracker: DatabaseTracker
    ) -> None:
        """A second write_env_entries call replaces the [env] section entirely."""
        tracker.write_database_config("postgres", "postgres")
        tracker.write_env_entries(
            "postgres", {"OLD_VAR": {"type": "user_input", "value": "x"}}
        )
        tracker.write_env_entries(
            "postgres", {"NEW_VAR": {"type": "user_input", "value": "y"}}
        )
        doc = tomlkit.loads(tracker._config_path("postgres").read_text()).unwrap()
        assert "NEW_VAR" in doc["env"]
        assert "OLD_VAR" not in doc["env"]


# ── read_database_config ──────────────────────────────────────────────────────


class TestReadDatabaseConfig:
    """Tests for DatabaseTracker.read_database_config."""

    def test_reads_written_config(self, tracker: DatabaseTracker) -> None:
        """read_database_config returns the same data that was written."""
        tracker.write_database_config("postgres", "postgres")
        doc = tracker.read_database_config("postgres").unwrap()
        assert doc["database"]["name"] == "postgres"

    def test_round_trip_with_env(self, tracker: DatabaseTracker) -> None:
        """Full write→read round-trip preserves both [database] and [env] sections."""
        tracker.write_database_config("postgres", "postgres")
        tracker.write_env_entries(
            "postgres",
            {
                "POSTGRES_PASSWORD": {"type": "secret"},
                "POSTGRES_DB": {"type": "user_input", "value": "postgres"},
            },
        )
        doc = tracker.read_database_config("postgres").unwrap()
        assert doc["database"]["name"] == "postgres"
        assert doc["env"]["POSTGRES_PASSWORD"]["type"] == "secret"
        assert "value" not in doc["env"]["POSTGRES_PASSWORD"]
        assert doc["env"]["POSTGRES_DB"]["value"] == "postgres"


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

    def test_remove_also_deletes_env_entries(self, tracker: DatabaseTracker) -> None:
        """The entire directory including env entries is removed."""
        tracker.write_database_config("postgres", "postgres")
        tracker.write_env_entries(
            "postgres", {"POSTGRES_DB": {"type": "user_input", "value": "postgres"}}
        )
        tracker.remove_database_config("postgres")
        assert not tracker._database_dir("postgres").exists()


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
