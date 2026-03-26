"""Unit tests for FeatureTracker."""

from pathlib import Path

import pytest
import tomlkit

from djdevx.utils.djdevx_config.backend.feature_tracker import FeatureTracker


@pytest.fixture
def tracker(tmp_path: Path) -> FeatureTracker:
    """
    Return a FeatureTracker whose djdevx_root is isolated to tmp_path/.djdevx.
    Uses a local subclass to override the property without touching the real filesystem.
    """
    djdevx_root = tmp_path / ".djdevx"
    djdevx_root.mkdir(parents=True)

    class IsolatedTracker(FeatureTracker):
        @property
        def djdevx_root(self) -> Path:  # type: ignore[override]
            return djdevx_root

    return IsolatedTracker()


# ── write_feature_config ──────────────────────────────────────────────────────


class TestWriteFeatureConfig:
    """Tests for FeatureTracker.write_feature_config."""

    def test_creates_config_toml(self, tracker: FeatureTracker) -> None:
        """write_feature_config creates the config.toml file."""
        tracker.write_feature_config("tailwind_theme", "Tailwind Theme")
        config = tracker._config_path("tailwind_theme")
        assert config.exists()

    def test_config_contains_feature_section(self, tracker: FeatureTracker) -> None:
        """config.toml contains a [feature] table with the correct name."""
        tracker.write_feature_config("tailwind_theme", "Tailwind Theme")
        doc = tomlkit.loads(tracker._config_path("tailwind_theme").read_text()).unwrap()
        assert doc["feature"]["name"] == "Tailwind Theme"

    def test_creates_parent_directories(self, tracker: FeatureTracker) -> None:
        """Intermediate directories are created for nested feature keys."""
        tracker.write_feature_config("css/bootstrap", "Bootstrap")
        assert tracker._config_path("css/bootstrap").exists()

    def test_overwrite_updates_name(self, tracker: FeatureTracker) -> None:
        """Calling write_feature_config twice updates the name in place."""
        tracker.write_feature_config("tailwind_theme", "Old Name")
        tracker.write_feature_config("tailwind_theme", "New Name")
        doc = tomlkit.loads(tracker._config_path("tailwind_theme").read_text()).unwrap()
        assert doc["feature"]["name"] == "New Name"

    def test_nested_css_key(self, tracker: FeatureTracker) -> None:
        """Nested keys like 'css/frankenui' store config at the right path."""
        tracker.write_feature_config("css/frankenui", "FrankenUI")
        expected_path = tracker._features_root / "css" / "frankenui" / "config.toml"
        assert expected_path.exists()


# ── read_feature_config ───────────────────────────────────────────────────────


class TestReadFeatureConfig:
    """Tests for FeatureTracker.read_feature_config."""

    def test_reads_written_config(self, tracker: FeatureTracker) -> None:
        """read_feature_config returns the same data that was written."""
        tracker.write_feature_config("pwa", "PWA")
        doc = tracker.read_feature_config("pwa").unwrap()
        assert doc["feature"]["name"] == "PWA"

    def test_nested_key_round_trip(self, tracker: FeatureTracker) -> None:
        """Nested feature keys survive a write/read round-trip."""
        tracker.write_feature_config("css/semantic", "Semantic UI")
        doc = tracker.read_feature_config("css/semantic").unwrap()
        assert doc["feature"]["name"] == "Semantic UI"


# ── remove_feature_config ─────────────────────────────────────────────────────


class TestRemoveFeatureConfig:
    """Tests for FeatureTracker.remove_feature_config."""

    def test_removes_tracking_directory(self, tracker: FeatureTracker) -> None:
        """remove_feature_config deletes the entire feature tracking directory."""
        tracker.write_feature_config("tailwind_ui", "Tailwind UI")
        assert tracker._feature_dir("tailwind_ui").exists()
        tracker.remove_feature_config("tailwind_ui")
        assert not tracker._feature_dir("tailwind_ui").exists()

    def test_noop_when_not_installed(self, tracker: FeatureTracker) -> None:
        """remove_feature_config does not raise when the feature was never installed."""
        tracker.remove_feature_config("nonexistent_feature")  # should not raise

    def test_removes_nested_feature(self, tracker: FeatureTracker) -> None:
        """Nested feature dirs are fully removed."""
        tracker.write_feature_config("css/bootstrap", "Bootstrap")
        tracker.remove_feature_config("css/bootstrap")
        assert not tracker._feature_dir("css/bootstrap").exists()


# ── is_installed ──────────────────────────────────────────────────────────────


class TestIsInstalled:
    """Tests for FeatureTracker.is_installed."""

    def test_returns_false_before_install(self, tracker: FeatureTracker) -> None:
        assert tracker.is_installed("tailwind_theme") is False

    def test_returns_true_after_write(self, tracker: FeatureTracker) -> None:
        tracker.write_feature_config("tailwind_theme", "Tailwind Theme")
        assert tracker.is_installed("tailwind_theme") is True

    def test_returns_false_after_remove(self, tracker: FeatureTracker) -> None:
        tracker.write_feature_config("tailwind_theme", "Tailwind Theme")
        tracker.remove_feature_config("tailwind_theme")
        assert tracker.is_installed("tailwind_theme") is False

    def test_nested_key_is_installed(self, tracker: FeatureTracker) -> None:
        tracker.write_feature_config("css/bootstrap", "Bootstrap")
        assert tracker.is_installed("css/bootstrap") is True

    def test_unrelated_features_are_independent(self, tracker: FeatureTracker) -> None:
        """Installing one feature does not affect is_installed for another."""
        tracker.write_feature_config("pwa", "PWA")
        assert tracker.is_installed("pwa") is True
        assert tracker.is_installed("tailwind_theme") is False


# ── features root path ────────────────────────────────────────────────────────


class TestFeaturesRoot:
    """Tests for the internal path helpers."""

    def test_features_root_path(self, tracker: FeatureTracker) -> None:
        expected = tracker.djdevx_root / "backend" / "django" / "features"
        assert tracker._features_root == expected

    def test_feature_dir_simple(self, tracker: FeatureTracker) -> None:
        expected = tracker.djdevx_root / "backend" / "django" / "features" / "pwa"
        assert tracker._feature_dir("pwa") == expected

    def test_feature_dir_nested(self, tracker: FeatureTracker) -> None:
        expected = (
            tracker.djdevx_root
            / "backend"
            / "django"
            / "features"
            / "css"
            / "bootstrap"
        )
        assert tracker._feature_dir("css/bootstrap") == expected
