"""Tests for list features command."""

from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from djdevx.backend.django.list import app

runner = CliRunner()


def test_list_features_no_features(temp_dir, monkeypatch):
    """Test listing features when none are installed."""
    monkeypatch.chdir(temp_dir)

    with patch("djdevx.backend.django.list.features.FeatureTracker") as mock_tracker:
        mock_instance = MagicMock()
        mock_instance._features_root = (
            temp_dir / ".djdevx" / "backend" / "django" / "features"
        )
        mock_tracker.return_value = mock_instance

        result = runner.invoke(app, ["features"])
        assert "No features installed yet" in result.output
        assert result.exit_code == 0


def test_list_features_with_features(temp_dir, monkeypatch):
    """Test listing features when some are installed."""
    monkeypatch.chdir(temp_dir)

    # Create feature directories with config.toml files
    features_root = temp_dir / ".djdevx" / "backend" / "django" / "features"
    features = [("tailwind_theme", "Tailwind Theme"), ("pwa", "PWA")]

    for feature_name, display_name in features:
        feature_dir = features_root / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        config_file = feature_dir / "config.toml"
        config_file.write_text(f'[feature]\nname = "{display_name}"\n')

    with patch("djdevx.backend.django.list.features.FeatureTracker") as mock_tracker:
        mock_instance = MagicMock()
        mock_instance._features_root = features_root
        mock_tracker.return_value = mock_instance

        result = runner.invoke(app, ["features"])
        assert "Installed features:" in result.output
        assert "Tailwind Theme" in result.output
        assert "PWA" in result.output
        assert result.exit_code == 0
