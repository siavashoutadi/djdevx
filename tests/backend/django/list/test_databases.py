"""Tests for list databases command."""

from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from djdevx.backend.django.list import app

runner = CliRunner()


def test_list_databases_no_databases(temp_dir, monkeypatch):
    """Test listing databases when none are installed."""
    monkeypatch.chdir(temp_dir)

    with patch("djdevx.backend.django.list.databases.DatabaseTracker") as mock_tracker:
        mock_instance = MagicMock()
        mock_instance._database_root = (
            temp_dir / ".djdevx" / "backend" / "django" / "database"
        )
        mock_tracker.return_value = mock_instance

        result = runner.invoke(app, ["databases"])
        assert "No databases installed yet" in result.output
        assert result.exit_code == 0


def test_list_databases_with_databases(temp_dir, monkeypatch):
    """Test listing databases when one is installed."""
    monkeypatch.chdir(temp_dir)

    database_root = temp_dir / ".djdevx" / "backend" / "django" / "database"
    database_dir = database_root / "postgres"
    database_dir.mkdir(parents=True, exist_ok=True)
    config_file = database_dir / "config.toml"
    config_file.write_text('[database]\nname = "postgres"\n')

    with patch("djdevx.backend.django.list.databases.DatabaseTracker") as mock_tracker:
        mock_instance = MagicMock()
        mock_instance._database_root = database_root
        mock_tracker.return_value = mock_instance

        result = runner.invoke(app, ["databases"])
        assert "Installed databases:" in result.output
        assert "postgres" in result.output
        assert result.exit_code == 0
