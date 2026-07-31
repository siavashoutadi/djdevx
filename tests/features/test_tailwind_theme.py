import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking._section import SectionTracking

runner = CliRunner()


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
        "tailwind_theme should be tracked"
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
