"""Tests for PWA feature functionality."""

import json
import os
import tempfile
from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from djdevx.main import app as main_app
from tests.test_helpers import create_test_django_backend

runner = CliRunner()


def create_test_icon(temp_dir: Path) -> Path:
    """Create a test icon for PWA generation."""
    icon_path = temp_dir / "test_icon.png"
    icon = Image.new("RGB", (512, 512), color="blue")
    icon.save(icon_path)
    return icon_path


def test_pwa_comprehensive(temp_dir):
    """Test comprehensive PWA functionality including installation, icon generation, manifest structure, and HTML modification."""
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Verify initial base.html doesn't have PWA links
    base_html_file = backend_dir / "templates" / "_base.html"
    initial_content = base_html_file.read_text()
    assert 'rel="manifest"' not in initial_content
    assert "apple_splash.html" not in initial_content

    with tempfile.TemporaryDirectory() as temp_icon_dir:
        temp_path = Path(temp_icon_dir)
        icon_path = create_test_icon(temp_path)

        # Install PWA with comprehensive configuration
        result = runner.invoke(
            main_app,
            [
                "backend",
                "django",
                "feature",
                "pwa",
                "--name",
                "Test PWA App",
                "--short-name",
                "TestPWA",
                "--description",
                "A test PWA application",
                "--icon-path",
                str(icon_path),
                "--background-color",
                "#ff0000",
                "--theme-color",
                "#00ff00",
                "--start-url",
                "/app/",
                "--dir",
                "rtl",
                "--scope",
                "/app/",
                "--orientation",
                "landscape",
                "--display",
                "fullscreen",
                "--language",
                "ar",
            ],
        )

        assert result.exit_code == 0, f"PWA install failed: {result.output}"

        project_dir = backend_dir

        # Verify PWA app files created
        pwa_apps_file = project_dir / "pwa" / "apps.py"
        assert pwa_apps_file.exists()
        pwa_views_file = project_dir / "pwa" / "views.py"
        assert pwa_views_file.exists()
        pwa_urls_file = project_dir / "pwa" / "urls.py"
        assert pwa_urls_file.exists()

        # Verify manifest.json created with correct structure and data
        manifest_file = project_dir / "pwa" / "templates" / "manifest.json"
        assert manifest_file.exists()

        with open(manifest_file, "r") as f:
            json_content = f.read()

        # Extract JSON part (skip the first line with {% load static %})
        json_lines = json_content.split("\n")[1:]
        json_content = "\n".join(json_lines)
        manifest_data = json.loads(json_content.strip())

        # Verify all manifest fields
        assert manifest_data["name"] == "Test PWA App"
        assert manifest_data["short_name"] == "TestPWA"
        assert manifest_data["description"] == "A test PWA application"
        assert manifest_data["background_color"] == "#ff0000"
        assert manifest_data["theme_color"] == "#00ff00"
        assert manifest_data["start_url"] == "/app/"
        assert manifest_data["dir"] == "rtl"
        assert manifest_data["scope"] == "/app/"
        assert manifest_data["orientation"] == "landscape"
        assert manifest_data["display"] == "fullscreen"
        assert manifest_data["lang"] == "ar"
        assert "icons" in manifest_data
        assert isinstance(manifest_data["icons"], list)
        assert len(manifest_data["icons"]) > 0

        # Verify icon entries have required fields
        for icon in manifest_data["icons"]:
            assert "src" in icon
            assert "sizes" in icon
            assert "type" in icon
            assert icon["type"] == "image/png"

        # Verify icon directories created
        android_icons_dir = project_dir / "static" / "images" / "icons" / "android"
        assert android_icons_dir.exists()
        ios_icons_dir = project_dir / "static" / "images" / "icons" / "ios"
        assert ios_icons_dir.exists()
        windows_icons_dir = project_dir / "static" / "images" / "icons" / "windows11"
        assert windows_icons_dir.exists()

        # Verify all expected Android icon sizes are generated
        expected_android_sizes = [48, 72, 96, 144, 192, 512]
        for size in expected_android_sizes:
            icon_file = android_icons_dir / f"android-launchericon-{size}x{size}.png"
            assert icon_file.exists(), f"Android icon {size}x{size} not found"
            # Verify the icon has correct dimensions
            with Image.open(icon_file) as img:
                assert img.size == (size, size)

        # Verify key iOS icon sizes are generated
        key_ios_sizes = [60, 120, 180, 1024]
        for size in key_ios_sizes:
            icon_file = ios_icons_dir / f"{size}.png"
            assert icon_file.exists(), f"iOS icon {size}x{size} not found"
            with Image.open(icon_file) as img:
                assert img.size == (size, size)

        # Verify splash screens generated
        splash_dir = project_dir / "static" / "images" / "icons" / "splash_screens"
        assert splash_dir.exists()
        splash_files = list(splash_dir.glob("*.png"))
        assert len(splash_files) > 10, "Not enough splash screen images generated"

        # Verify apple splash include file created
        apple_splash_file = project_dir / "templates" / "apple_splash.html"
        assert apple_splash_file.exists()

        # Verify base.html was modified correctly
        modified_content = base_html_file.read_text()
        assert 'rel="manifest"' in modified_content
        assert 'href="/manifest.json"' in modified_content
        assert '{% include "apple_splash.html" %}' in modified_content

        # Verify the modifications are before </head>
        head_close_index = modified_content.find("</head>")
        manifest_index = modified_content.find('rel="manifest"')
        splash_index = modified_content.find("apple_splash.html")
        assert head_close_index > manifest_index > 0
        assert head_close_index > splash_index > 0

        # Verify settings and URL files created
        settings_file = project_dir / "settings" / "apps" / "pwa.py"
        assert settings_file.exists()
        urls_file = project_dir / "urls" / "apps" / "pwa.py"
        assert urls_file.exists()


def test_pwa_invalid_icon_path(temp_dir):
    """Test PWA installation with invalid icon path."""
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        main_app,
        [
            "backend",
            "django",
            "feature",
            "pwa",
            "--name",
            "Test PWA",
            "--short-name",
            "Test",
            "--description",
            "Test app",
            "--icon-path",
            "/non/existent/path.png",
            "--background-color",
            "#ffffff",
            "--theme-color",
            "#000000",
            "--start-url",
            "/",
            "--dir",
            "ltr",
            "--orientation",
            "portrait",
            "--display",
            "standalone",
            "--language",
            "en",
        ],
    )

    assert result.exit_code != 0
