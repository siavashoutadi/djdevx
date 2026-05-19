"""Unit tests for CacheTracker."""

from pathlib import Path

import pytest
import tomlkit

from djdevx.utils.djdevx_config.backend.cache_tracker import CacheTracker


@pytest.fixture
def tracker(tmp_path: Path) -> CacheTracker:
    """
    Return a CacheTracker whose djdevx_root is isolated to tmp_path/.djdevx.
    Uses a local subclass to override the property without touching the real filesystem.
    """
    djdevx_root = tmp_path / ".djdevx"
    djdevx_root.mkdir(parents=True)

    class IsolatedTracker(CacheTracker):
        @property
        def djdevx_root(self) -> Path:  # type: ignore[override]
            return djdevx_root

    return IsolatedTracker()


# ── write_cache_config ────────────────────────────────────────────────────────


class TestWriteCacheConfig:
    """Tests for CacheTracker.write_cache_config."""

    def test_creates_config_toml(self, tracker: CacheTracker) -> None:
        """write_cache_config creates the config.toml file."""
        tracker.write_cache_config("redis", "redis")
        assert tracker._config_path("redis").exists()

    def test_config_contains_cache_section(self, tracker: CacheTracker) -> None:
        """config.toml contains a [cache] table with the correct name."""
        tracker.write_cache_config("redis", "redis")
        doc = tomlkit.loads(tracker._config_path("redis").read_text()).unwrap()
        assert doc["cache"]["name"] == "redis"

    def test_creates_parent_directories(self, tracker: CacheTracker) -> None:
        """Intermediate directories are created automatically."""
        tracker.write_cache_config("redis", "redis")
        assert tracker._config_path("redis").exists()

    def test_overwrite_updates_name(self, tracker: CacheTracker) -> None:
        """Calling write_cache_config twice updates the name in place."""
        tracker.write_cache_config("redis", "old name")
        tracker.write_cache_config("redis", "redis")
        doc = tomlkit.loads(tracker._config_path("redis").read_text()).unwrap()
        assert doc["cache"]["name"] == "redis"

    def test_overwrite_preserves_env_section(self, tracker: CacheTracker) -> None:
        """Re-writing [cache] does not discard an existing [env] section."""
        tracker.write_cache_config("redis", "redis")
        tracker.write_env_entries(
            "redis",
            {
                "CACHE_LOCATION": {
                    "type": "user_input",
                    "value": "redis://default@cache:6379/1",
                }
            },
        )
        tracker.write_cache_config("redis", "redis")
        doc = tomlkit.loads(tracker._config_path("redis").read_text()).unwrap()
        assert "env" in doc, "[env] section was lost after re-writing [cache]"


# ── write_env_entries ─────────────────────────────────────────────────────────


class TestWriteEnvEntries:
    """Tests for CacheTracker.write_env_entries."""

    def test_writes_user_input_with_value(self, tracker: CacheTracker) -> None:
        """user_input entries are written with their value."""
        tracker.write_cache_config("redis", "redis")
        tracker.write_env_entries(
            "redis",
            {
                "CACHE_LOCATION": {
                    "type": "user_input",
                    "value": "redis://default@cache:6379/1",
                },
            },
        )
        doc = tomlkit.loads(tracker._config_path("redis").read_text()).unwrap()
        assert doc["env"]["CACHE_LOCATION"]["type"] == "user_input"
        assert doc["env"]["CACHE_LOCATION"]["value"] == "redis://default@cache:6379/1"

    def test_writes_secret_without_value(self, tracker: CacheTracker) -> None:
        """Secret entries are written with type only — value is never stored."""
        tracker.write_cache_config("redis", "redis")
        tracker.write_env_entries(
            "redis",
            {
                "REDIS_PASSWORD": {"type": "secret"},
            },
        )
        doc = tomlkit.loads(tracker._config_path("redis").read_text()).unwrap()
        assert doc["env"]["REDIS_PASSWORD"]["type"] == "secret"
        assert "value" not in doc["env"]["REDIS_PASSWORD"]

    def test_writes_all_redis_env_vars(self, tracker: CacheTracker) -> None:
        """Both Redis env vars are written correctly."""
        tracker.write_cache_config("redis", "redis")
        tracker.write_env_entries(
            "redis",
            {
                "REDIS_PASSWORD": {"type": "secret"},
                "CACHE_LOCATION": {
                    "type": "user_input",
                    "value": "redis://default@cache:6379/1",
                },
            },
        )
        doc = tomlkit.loads(tracker._config_path("redis").read_text()).unwrap()
        assert set(doc["env"].keys()) == {"REDIS_PASSWORD", "CACHE_LOCATION"}

    def test_env_preserves_cache_section(self, tracker: CacheTracker) -> None:
        """Writing [env] does not discard the existing [cache] section."""
        tracker.write_cache_config("redis", "redis")
        tracker.write_env_entries(
            "redis",
            {
                "CACHE_LOCATION": {
                    "type": "user_input",
                    "value": "redis://default@cache:6379/1",
                },
            },
        )
        doc = tomlkit.loads(tracker._config_path("redis").read_text()).unwrap()
        assert doc["cache"]["name"] == "redis"

    def test_env_section_is_replaced_on_second_call(
        self, tracker: CacheTracker
    ) -> None:
        """A second write_env_entries call replaces the [env] section entirely."""
        tracker.write_cache_config("redis", "redis")
        tracker.write_env_entries(
            "redis", {"OLD_VAR": {"type": "user_input", "value": "x"}}
        )
        tracker.write_env_entries(
            "redis", {"NEW_VAR": {"type": "user_input", "value": "y"}}
        )
        doc = tomlkit.loads(tracker._config_path("redis").read_text()).unwrap()
        assert "NEW_VAR" in doc["env"]
        assert "OLD_VAR" not in doc["env"]


# ── read_cache_config ─────────────────────────────────────────────────────────


class TestReadCacheConfig:
    """Tests for CacheTracker.read_cache_config."""

    def test_reads_written_config(self, tracker: CacheTracker) -> None:
        """read_cache_config returns the same data that was written."""
        tracker.write_cache_config("redis", "redis")
        doc = tracker.read_cache_config("redis").unwrap()
        assert doc["cache"]["name"] == "redis"

    def test_round_trip_with_env(self, tracker: CacheTracker) -> None:
        """Full write→read round-trip preserves both [cache] and [env] sections."""
        tracker.write_cache_config("redis", "redis")
        tracker.write_env_entries(
            "redis",
            {
                "REDIS_PASSWORD": {"type": "secret"},
                "CACHE_LOCATION": {
                    "type": "user_input",
                    "value": "redis://default@cache:6379/1",
                },
            },
        )
        doc = tracker.read_cache_config("redis").unwrap()
        assert doc["cache"]["name"] == "redis"
        assert doc["env"]["REDIS_PASSWORD"]["type"] == "secret"
        assert "value" not in doc["env"]["REDIS_PASSWORD"]
        assert doc["env"]["CACHE_LOCATION"]["value"] == "redis://default@cache:6379/1"


# ── remove_cache_config ───────────────────────────────────────────────────────


class TestRemoveCacheConfig:
    """Tests for CacheTracker.remove_cache_config."""

    def test_removes_tracking_directory(self, tracker: CacheTracker) -> None:
        """remove_cache_config deletes the entire cache tracking directory."""
        tracker.write_cache_config("redis", "redis")
        assert tracker._cache_dir("redis").exists()
        tracker.remove_cache_config("redis")
        assert not tracker._cache_dir("redis").exists()

    def test_noop_when_not_installed(self, tracker: CacheTracker) -> None:
        """remove_cache_config does not raise when the cache was never installed."""
        tracker.remove_cache_config("redis")  # should not raise

    def test_remove_also_deletes_env_entries(self, tracker: CacheTracker) -> None:
        """The entire directory including env entries is removed."""
        tracker.write_cache_config("redis", "redis")
        tracker.write_env_entries(
            "redis",
            {
                "CACHE_LOCATION": {
                    "type": "user_input",
                    "value": "redis://default@cache:6379/1",
                }
            },
        )
        tracker.remove_cache_config("redis")
        assert not tracker._cache_dir("redis").exists()


# ── is_installed ──────────────────────────────────────────────────────────────


class TestIsInstalled:
    """Tests for CacheTracker.is_installed."""

    def test_returns_false_before_install(self, tracker: CacheTracker) -> None:
        assert tracker.is_installed("redis") is False

    def test_returns_true_after_write(self, tracker: CacheTracker) -> None:
        tracker.write_cache_config("redis", "redis")
        assert tracker.is_installed("redis") is True

    def test_returns_false_after_remove(self, tracker: CacheTracker) -> None:
        tracker.write_cache_config("redis", "redis")
        tracker.remove_cache_config("redis")
        assert tracker.is_installed("redis") is False

    def test_unrelated_caches_are_independent(self, tracker: CacheTracker) -> None:
        """Installing one cache does not affect is_installed for another."""
        tracker.write_cache_config("redis", "redis")
        assert tracker.is_installed("redis") is True
        assert tracker.is_installed("memcached") is False


# ── path helpers ──────────────────────────────────────────────────────────────


class TestCacheRoot:
    """Tests for the internal path helpers."""

    def test_cache_root_path(self, tracker: CacheTracker) -> None:
        expected = tracker.djdevx_root / "backend" / "django" / "cache"
        assert tracker._cache_root == expected

    def test_cache_dir(self, tracker: CacheTracker) -> None:
        expected = tracker.djdevx_root / "backend" / "django" / "cache" / "redis"
        assert tracker._cache_dir("redis") == expected

    def test_config_path(self, tracker: CacheTracker) -> None:
        expected = (
            tracker.djdevx_root
            / "backend"
            / "django"
            / "cache"
            / "redis"
            / "config.toml"
        )
        assert tracker._config_path("redis") == expected
