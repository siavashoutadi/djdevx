"""Tests for PWA feature functionality."""

import os

from typer.testing import CliRunner

from djdevx.main import app as main_app
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking import ProjectTracking, Section

runner = CliRunner()


def test_pwa_comprehensive(temp_dir):
    """Test PWA installation and removal."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        main_app,
        [
            "features",
            "add",
            "pwa",
        ],
    )

    assert result.exit_code == 0, f"PWA install failed: {result.output}"

    pwa_apps_file = temp_dir / "pwa" / "apps.py"
    assert pwa_apps_file.exists()
    pwa_views_file = temp_dir / "pwa" / "views.py"
    assert pwa_views_file.exists()
    pwa_urls_file = temp_dir / "pwa" / "urls.py"
    assert pwa_urls_file.exists()

    sw_file = temp_dir / "pwa" / "templates" / "sw.js"
    assert sw_file.exists()

    settings_file = temp_dir / "settings" / "apps" / "pwa.py"
    assert settings_file.exists()
    urls_file = temp_dir / "urls" / "apps" / "pwa.py"
    assert urls_file.exists()

    assert ProjectTracking().is_installed(Section.FEATURES, "pwa"), (
        "PWA should be tracked after install"
    )

    result = runner.invoke(main_app, ["features", "remove", "pwa"])
    assert result.exit_code == 0, f"PWA remove failed: {result.output}"

    assert not ProjectTracking().is_installed(Section.FEATURES, "pwa"), (
        "PWA tracking should be removed"
    )


def test_pwa_invalid_icon_path(temp_dir):
    """Test PWA installation succeeds (no icon path option in new CLI)."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        main_app,
        [
            "features",
            "add",
            "pwa",
        ],
    )

    assert result.exit_code == 0
