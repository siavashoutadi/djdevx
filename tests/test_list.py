"""Tests for list commands across modules."""

from typer.testing import CliRunner

from djdevx.main import app

runner = CliRunner()


def setup_project_dir(temp_dir):
    """Create a minimal djdevx.toml."""
    djdevx = temp_dir / "djdevx.toml"
    djdevx.write_text('project_name = "test"\n')
    return temp_dir


def test_packages_list_no_packages(temp_dir, monkeypatch):
    """Test listing packages when none are installed."""
    setup_project_dir(temp_dir)
    monkeypatch.chdir(temp_dir)
    result = runner.invoke(app, ["packages", "list"])
    assert result.exit_code == 0
    assert "Packages" in result.output
    assert "✗" in result.output
    assert "whitenoise" in result.output


def test_frameworks_list_no_frameworks(temp_dir, monkeypatch):
    """Test listing frameworks when none are installed."""
    setup_project_dir(temp_dir)
    monkeypatch.chdir(temp_dir)
    result = runner.invoke(app, ["frameworks", "list"])
    assert result.exit_code == 0
    assert "Frameworks" in result.output
    assert "✗" in result.output
    assert "bootstrap" in result.output


def test_features_list_no_features(temp_dir, monkeypatch):
    """Test listing features when none are installed."""
    setup_project_dir(temp_dir)
    monkeypatch.chdir(temp_dir)
    result = runner.invoke(app, ["features", "list"])
    assert result.exit_code == 0
    assert "Features" in result.output
    assert "✗" in result.output
    assert "pwa" in result.output


def test_database_list_no_databases(temp_dir, monkeypatch):
    """Test listing databases when none are installed."""
    setup_project_dir(temp_dir)
    monkeypatch.chdir(temp_dir)
    result = runner.invoke(app, ["database", "list"])
    assert result.exit_code == 0
    assert "Databases" in result.output
    assert "✗" in result.output
    assert "postgres" in result.output


def test_cache_list_no_caches(temp_dir, monkeypatch):
    """Test listing caches when none are installed."""
    setup_project_dir(temp_dir)
    monkeypatch.chdir(temp_dir)
    result = runner.invoke(app, ["cache", "list"])
    assert result.exit_code == 0
    assert "Caches" in result.output
    assert "✗" in result.output
    assert "redis" in result.output
