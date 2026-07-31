from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django_tailwind_cli"


def test_django_tailwind_cli_install_and_remove(temp_dir):
    """
    Test django-tailwind-cli package installation and removal.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "django_tailwind_cli",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    settings_file = temp_dir / "settings" / "packages" / "django_tailwind_cli.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "django_tailwind_cli.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    dark_mode_template = temp_dir / "templates" / "_tw_dark_mode.html"
    assert dark_mode_template.exists(), "Dark mode template not created"

    expected_dark_mode = DATA_DIR / "templates" / "_tw_dark_mode.html"
    expected_content = expected_dark_mode.read_text()
    actual_content = dark_mode_template.read_text()
    assert actual_content == expected_content, "Dark mode template content mismatch"

    input_css = temp_dir / "tailwind" / "src" / "css" / "input.css"
    assert input_css.exists(), "input.css not created"

    expected_input_css = DATA_DIR / "tailwind" / "src" / "css" / "input.css"
    expected_content = expected_input_css.read_text()
    actual_content = input_css.read_text()
    assert actual_content == expected_content, "input.css content mismatch"

    base_template = temp_dir / "templates" / "_base.html"
    assert base_template.exists(), "Base template not found"

    template_content = base_template.read_text()
    assert "{% include './_tw_dark_mode.html' %}" in template_content, (
        "Dark mode include not added to base template"
    )

    gitignore = temp_dir / ".gitignore"
    if gitignore.exists():
        gitignore_content = gitignore.read_text()
        assert (
            "tailwind" in gitignore_content.lower()
            or "node_modules" in gitignore_content
        ), "tailwind entries not added to .gitignore"

    dockerfile = temp_dir / "Dockerfile"
    if dockerfile.exists():
        dockerfile_content = dockerfile.read_text()
        assert (
            "tailwind" in dockerfile_content.lower()
            or "node" in dockerfile_content.lower()
        ), "tailwind entries not added to Dockerfile"

    assert PixiRunner().has_dependency("django-tailwind-cli"), (
        "django-tailwind-cli dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "django_tailwind_cli",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not settings_file.exists(), "Settings file not removed"
    assert not dark_mode_template.exists(), "Dark mode template not removed"
    assert not input_css.exists(), "input.css not removed"

    assert not PixiRunner().has_dependency("django-tailwind-cli"), (
        "django-tailwind-cli dependency found after removal"
    )
