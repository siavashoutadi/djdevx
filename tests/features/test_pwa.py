"""Tests for PWA feature functionality."""

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from djdevx.main import app as main_app
from djdevx.providers.features.pwa import PWAFeature
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking import ProjectTracking, Section

runner = CliRunner()


def _make_project(temp_dir: Path) -> Path:
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    return temp_dir


def test_pwa_comprehensive(temp_dir):
    """Test PWA installation and removal."""
    _make_project(temp_dir)

    result = runner.invoke(main_app, ["features", "add", "pwa"])

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

    # default PNG icon must actually generate raster icons
    android_192 = (
        temp_dir
        / "static"
        / "images"
        / "icons"
        / "android"
        / "android-launchericon-192x192.png"
    )
    assert android_192.exists(), "PWA icons should be generated from logo.png"
    assert (temp_dir / "static" / "images" / "icons" / "ios" / "512.png").exists()
    manifest = temp_dir / "pwa" / "templates" / "manifest.json"
    assert "android-launchericon-192x192.png" in manifest.read_text()

    result = runner.invoke(main_app, ["features", "remove", "pwa"])
    assert result.exit_code == 0, f"PWA remove failed: {result.output}"

    assert not ProjectTracking().is_installed(Section.FEATURES, "pwa"), (
        "PWA tracking should be removed"
    )


def test_pwa_default_icon(temp_dir):
    """Test PWA installation succeeds with the default PNG icon."""
    _make_project(temp_dir)

    result = runner.invoke(main_app, ["features", "add", "pwa"])

    assert result.exit_code == 0


def test_pwa_missing_icon_aborts_install(temp_dir):
    """Installation must abort — without touching anything — when the icon is gone."""
    root = _make_project(temp_dir)
    (root / "static" / "images" / "logo.png").unlink()

    result = runner.invoke(main_app, ["features", "add", "pwa"])

    assert result.exit_code != 0
    assert "Icon file not found" in result.output
    assert not ProjectTracking().is_installed(Section.FEATURES, "pwa"), (
        "PWA must not be tracked when the install aborted"
    )
    assert not (root / "pwa" / "apps.py").exists(), (
        "Aborted install must not copy templates"
    )


def _feature(root: Path, icon_path: str) -> PWAFeature:
    feature = PWAFeature()
    feature._install_context = {"icon_path": icon_path}
    return feature


def test_pwa_empty_icon_rejected(temp_dir):
    """An empty icon path must abort the install."""
    _make_project(temp_dir)
    feature = _feature(temp_dir, "")

    with pytest.raises(ValueError, match="needs an icon"):
        feature.before_pixi_install()


def test_pwa_svg_icon_rejected(temp_dir):
    """SVG icons must be rejected with a clear message."""
    _make_project(temp_dir)
    feature = _feature(temp_dir, "static/images/logo.svg")

    with pytest.raises(ValueError, match="SVG icons are not supported"):
        feature.before_pixi_install()
