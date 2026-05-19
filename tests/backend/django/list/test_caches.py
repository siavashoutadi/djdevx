"""Tests for list caches command."""

from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from djdevx.backend.django.list import app

runner = CliRunner()


def test_list_caches_no_caches(temp_dir, monkeypatch):
    """Test listing caches when none are installed."""
    monkeypatch.chdir(temp_dir)

    with patch("djdevx.backend.django.list.caches.CacheTracker") as mock_tracker:
        mock_instance = MagicMock()
        mock_instance._cache_root = (
            temp_dir / ".djdevx" / "backend" / "django" / "cache"
        )
        mock_tracker.return_value = mock_instance

        result = runner.invoke(app, ["caches"])
        assert "No caches installed yet" in result.output
        assert result.exit_code == 0


def test_list_caches_with_caches(temp_dir, monkeypatch):
    """Test listing caches when one is installed."""
    monkeypatch.chdir(temp_dir)

    cache_root = temp_dir / ".djdevx" / "backend" / "django" / "cache"
    cache_dir = cache_root / "redis"
    cache_dir.mkdir(parents=True, exist_ok=True)
    config_file = cache_dir / "config.toml"
    config_file.write_text('[cache]\nname = "redis"\n')

    with patch("djdevx.backend.django.list.caches.CacheTracker") as mock_tracker:
        mock_instance = MagicMock()
        mock_instance._cache_root = cache_root
        mock_tracker.return_value = mock_instance

        result = runner.invoke(app, ["caches"])
        assert "Installed caches:" in result.output
        assert "redis" in result.output
        assert result.exit_code == 0
