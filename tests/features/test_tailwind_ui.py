import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking._section import SectionTracking
from djdevx.utils.project.pixi_runner import PixiRunner

runner = CliRunner()


def test_tailwind_ui_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["packages", "add", "heroicons"])
    assert result.exit_code == 0, f"Heroicons install failed: {result.output}"

    result = runner.invoke(app, ["packages", "add", "django_tailwind_cli"])
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "features",
            "add",
            "tailwind_theme",
        ],
    )
    assert result.exit_code == 0, f"Tailwind theme install failed: {result.output}"

    result = runner.invoke(app, ["features", "add", "tailwind_ui"])
    assert result.exit_code == 0, f"Tailwind UI install failed: {result.output}"

    tailwind_ui_app_dir = temp_dir / "tailwind_ui"
    assert tailwind_ui_app_dir.exists(), "tailwind_ui app directory not created"

    apps_file = tailwind_ui_app_dir / "apps.py"
    assert apps_file.exists(), "tailwind_ui apps.py not created"

    views_file = tailwind_ui_app_dir / "views.py"
    assert views_file.exists(), "tailwind_ui views.py not created"

    urls_file = tailwind_ui_app_dir / "urls.py"
    assert urls_file.exists(), "tailwind_ui urls.py not created"

    tailwind_ui_css_dir = temp_dir / "tailwind" / "src" / "css" / "tailwind-ui"
    assert tailwind_ui_css_dir.exists(), "tailwind-ui CSS directory not created"

    all_css_file = tailwind_ui_css_dir / "all.css"
    assert all_css_file.exists(), "tailwind-ui all.css not created"

    settings_file = temp_dir / "settings" / "apps" / "tailwind_ui.py"
    assert settings_file.exists(), "tailwind_ui settings file not created"

    urls_config_file = temp_dir / "urls" / "apps" / "tailwind_ui.py"
    assert urls_config_file.exists(), "tailwind_ui URLs config file not created"

    input_css_file = temp_dir / "tailwind" / "src" / "css" / "input.css"
    input_content = input_css_file.read_text()
    assert '@import "./tailwind-ui/all.css";' in input_content, (
        "tailwind-ui import not added to input.css"
    )

    assert SectionTracking("features").is_installed("tailwind-ui"), (
        "tailwind_ui should be tracked after install"
    )

    result = runner.invoke(app, ["features", "remove", "tailwind-ui"])
    assert result.exit_code == 0, f"Tailwind UI remove failed: {result.output}"

    assert not tailwind_ui_app_dir.exists(), "tailwind_ui app directory not removed"
    assert not tailwind_ui_css_dir.exists(), "tailwind-ui CSS directory not removed"
    assert not settings_file.exists(), "tailwind_ui settings file not removed"
    assert not urls_config_file.exists(), "tailwind_ui URLs config file not removed"

    input_content_after = input_css_file.read_text()
    assert '@import "./tailwind-ui/all.css";' not in input_content_after, (
        "tailwind-ui import not removed from input.css"
    )

    assert not SectionTracking("features").is_installed("tailwind-ui"), (
        "tailwind_ui tracking should be removed"
    )


def test_tailwind_ui_missing_deps(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["features", "add", "tailwind_ui"])
    assert result.exit_code == 0, f"Tailwind UI install failed: {result.output}"
    assert PixiRunner().has_dependency("django-tailwind-cli"), (
        "Required package django-tailwind-cli should be auto-installed"
    )


def test_tailwind_ui_remove_when_not_installed(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["features", "remove", "tailwind-ui"])
    assert result.exit_code == 0


def test_tailwind_theme_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["packages", "add", "django_tailwind_cli"])
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "features",
            "add",
            "tailwind_theme",
        ],
    )
    assert result.exit_code == 0, f"Install failed: {result.output}"

    theme_css_file = temp_dir / "tailwind" / "src" / "css" / "theme.css"
    input_css_file = temp_dir / "tailwind" / "src" / "css" / "input.css"

    assert theme_css_file.exists(), "theme.css file should be created"
    theme_content = theme_css_file.read_text()
    assert "--color-primary-50:" in theme_content, (
        "Primary color palette should be generated"
    )

    input_content = input_css_file.read_text()
    assert '@import "./theme.css";' in input_content, (
        "Theme import should be added to input.css"
    )

    assert SectionTracking("features").is_installed("tailwind-theme"), (
        "tailwind_theme should be tracked after install"
    )

    result = runner.invoke(app, ["features", "remove", "tailwind-theme"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not theme_css_file.exists(), "theme.css file should be removed"
    input_content = input_css_file.read_text()
    assert '@import "./theme.css";' not in input_content, (
        "Theme import should be removed"
    )

    assert not SectionTracking("features").is_installed("tailwind-theme"), (
        "tracking should be removed"
    )


def test_tailwind_theme_remove_when_not_installed(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    result = runner.invoke(app, ["features", "remove", "tailwind-theme"])
    assert result.exit_code == 0
