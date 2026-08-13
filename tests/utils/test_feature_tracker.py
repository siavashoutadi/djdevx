"""Unit tests for SectionTracking (features)."""

import tomllib
from pathlib import Path

import pytest

from djdevx.utils.tracking._section import SectionTracking


@pytest.fixture
def tracking(tmp_path: Path) -> SectionTracking:
    """Return a SectionTracking instance isolated to tmp_path with a djdevx.toml."""
    djdevx = tmp_path / "djdevx.toml"
    djdevx.write_text('project_name = "test"\n')
    return SectionTracking("features", project_root=tmp_path)


# ── add ────────────────────────────────────────────────────────────────────────


class TestAdd:
    """Tests for SectionTracking.add."""

    def test_add_creates_tracking_entry(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        assert tracking.is_installed("pwa") is True

    def test_add_writes_to_djdevx_toml(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        djdevx_path = tracking._project._djdevx_path
        doc = tomllib.loads(djdevx_path.read_text())
        assert doc["features"]["pwa"]["display_name"] == "PWA"

    def test_add_idempotent(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        tracking.add("pwa", "PWA")
        installed = tracking.list()
        assert list(installed.keys()).count("pwa") == 1


# ── remove ─────────────────────────────────────────────────────────────────────


class TestRemove:
    """Tests for SectionTracking.remove."""

    def test_remove_deletes_tracking_entry(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        tracking.remove("pwa")
        assert tracking.is_installed("pwa") is False

    def test_remove_is_noop_when_not_installed(self, tracking: SectionTracking) -> None:
        tracking.remove("pwa")  # should not raise

    def test_remove_only_affects_specified(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        tracking.add("cache", "Cache")
        tracking.remove("pwa")
        assert tracking.is_installed("pwa") is False
        assert tracking.is_installed("cache") is True


# ── is_installed ──────────────────────────────────────────────────────────────


class TestIsInstalled:
    """Tests for SectionTracking.is_installed."""

    def test_returns_false_before_install(self, tracking: SectionTracking) -> None:
        assert tracking.is_installed("pwa") is False

    def test_returns_true_after_add(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        assert tracking.is_installed("pwa") is True

    def test_returns_false_after_remove(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        tracking.remove("pwa")
        assert tracking.is_installed("pwa") is False

    def test_unrelated_features_are_independent(
        self, tracking: SectionTracking
    ) -> None:
        tracking.add("pwa", "PWA")
        assert tracking.is_installed("pwa") is True
        assert tracking.is_installed("cache") is False


# ── list ──────────────────────────────────────────────────────────────────────


class TestList:
    """Tests for SectionTracking.list."""

    def test_empty_list(self, tracking: SectionTracking) -> None:
        assert tracking.list() == {}

    def test_list_with_one_entry(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        result = tracking.list()
        assert "pwa" in result
        assert result["pwa"]["display_name"] == "PWA"

    def test_list_with_multiple_entries(self, tracking: SectionTracking) -> None:
        tracking.add("pwa", "PWA")
        tracking.add("cache", "Cache")
        result = tracking.list()
        assert len(result) == 2
        assert "pwa" in result
        assert "cache" in result
