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


# ── read_cache_config ─────────────────────────────────────────────────────────


class TestReadCacheConfig:
    """Tests for CacheTracker.read_cache_config."""

    def test_reads_written_config(self, tracker: CacheTracker) -> None:
        """read_cache_config returns the same data that was written."""
        tracker.write_cache_config("redis", "redis")
        doc = tracker.read_cache_config("redis").unwrap()
        assert doc["cache"]["name"] == "redis"


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
