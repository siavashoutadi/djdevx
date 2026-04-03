"""Tests for list packages command."""

from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from djdevx.backend.django.list import app

runner = CliRunner()


def test_list_packages_no_packages(temp_dir, monkeypatch):
    """Test listing packages when none are installed."""
    monkeypatch.chdir(temp_dir)

    with patch("djdevx.backend.django.list.packages.ProjectConfig") as mock_config:
        mock_instance = MagicMock()
        mock_instance.djdevx_root = temp_dir / ".djdevx"
        mock_config.return_value = mock_instance

        result = runner.invoke(app, ["packages"])
        assert "No packages installed yet" in result.output
        assert result.exit_code == 0


def test_list_packages_with_packages(temp_dir, monkeypatch):
    """Test listing packages when some are installed."""
    monkeypatch.chdir(temp_dir)

    # Create package directories with config.toml files
    packages_root = temp_dir / ".djdevx" / "backend" / "django" / "packages"
    packages = [
        ("djangorestframework", "Django REST Framework"),
        ("django_cors_headers", "django-cors-headers"),
    ]

    for package_name, display_name in packages:
        package_dir = packages_root / package_name
        package_dir.mkdir(parents=True, exist_ok=True)
        config_file = package_dir / "config.toml"
        config_file.write_text(f'[package]\nname = "{display_name}"\n')

    with patch("djdevx.backend.django.list.packages.ProjectConfig") as mock_config:
        mock_instance = MagicMock()
        mock_instance.djdevx_root = temp_dir / ".djdevx"
        mock_config.return_value = mock_instance

        result = runner.invoke(app, ["packages"])
        assert "Installed packages:" in result.output
        assert "Django REST Framework" in result.output
        assert "django-cors-headers" in result.output
        assert result.exit_code == 0
