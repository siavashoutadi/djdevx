from pathlib import Path
import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.django.project_manager import DjangoProjectManager
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "django_tailwind_cli"


def test_django_tailwind_cli_install_and_remove(temp_dir):
    """
    Test django-tailwind-cli package installation and removal.
    """

    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-tailwind-cli",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    # Check settings file
    settings_file = backend_dir / "settings" / "packages" / "django_tailwind_cli.py"
    assert settings_file.exists(), "Settings file not created"

    expected_settings_file = (
        DATA_DIR / "settings" / "packages" / "django_tailwind_cli.py"
    )
    expected_content = expected_settings_file.read_text()
    actual_content = settings_file.read_text()
    assert actual_content == expected_content, "Settings content mismatch"

    # Check template files
    dark_mode_template = backend_dir / "templates" / "_tw_dark_mode.html"
    assert dark_mode_template.exists(), "Dark mode template not created"

    expected_dark_mode_file = DATA_DIR / "templates" / "_tw_dark_mode.html"
    expected_dark_mode_content = expected_dark_mode_file.read_text()
    actual_dark_mode_content = dark_mode_template.read_text()
    assert actual_dark_mode_content == expected_dark_mode_content, (
        "Dark mode template content mismatch"
    )

    # Check tailwind CSS input file
    input_css_file = backend_dir / "tailwind" / "src" / "css" / "input.css"
    assert input_css_file.exists(), "Tailwind input.css not created"

    expected_input_css_file = DATA_DIR / "tailwind" / "src" / "css" / "input.css"
    expected_input_css_content = expected_input_css_file.read_text()
    actual_input_css_content = input_css_file.read_text()
    assert actual_input_css_content == expected_input_css_content, (
        "Input CSS content mismatch"
    )

    # Check base template modifications
    base_template_path = backend_dir / "templates" / "_base.html"
    if base_template_path.exists():
        base_content = base_template_path.read_text()
        assert "{% load tailwind_cli %}" in base_content, (
            "Tailwind template tag not added to base template"
        )
        assert "{% tailwind_css %}" in base_content, (
            "Tailwind CSS tag not added to base template"
        )
        assert '{% include "./_tw_dark_mode.html" %}' in base_content, (
            "Dark mode include not added to base template"
        )

    # Check gitignore modifications
    gitignore_path = backend_dir / ".gitignore"
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        assert "/static/css/tailwind.min.css" in gitignore_content, (
            "Tailwind output CSS not added to gitignore"
        )

    # Check Dockerfile modifications
    dockerfile_path = backend_dir / "Dockerfile"
    if dockerfile_path.exists():
        dockerfile_content = dockerfile_path.read_text()
        assert "uv run manage.py tailwind build" in dockerfile_content, (
            "Tailwind build command not added to Dockerfile"
        )

    assert DjangoProjectManager().has_dependency("django-tailwind-cli"), (
        "django-tailwind-cli dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "packages",
            "django-tailwind-cli",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    # Check that files were removed
    assert not settings_file.exists(), "Settings file not removed"
    assert not dark_mode_template.exists(), "Dark mode template not removed"
    assert not input_css_file.exists(), "Tailwind input.css not removed"

    # Check that base template modifications were removed
    if base_template_path.exists():
        base_content = base_template_path.read_text()
        assert "{% load tailwind_cli %}" not in base_content, (
            "Tailwind template tag not removed from base template"
        )
        assert "{% tailwind_css %}" not in base_content, (
            "Tailwind CSS tag not removed from base template"
        )
        assert '{% include "./_tw_dark_mode.html" %}' not in base_content, (
            "Dark mode include not removed from base template"
        )

    # Check that gitignore modifications were removed
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        assert "/static/css/tailwind.min.css" not in gitignore_content, (
            "Tailwind output CSS not removed from gitignore"
        )

    # Check that Dockerfile modifications were removed
    if dockerfile_path.exists():
        dockerfile_content = dockerfile_path.read_text()
        assert "uv run manage.py tailwind build" not in dockerfile_content, (
            "Tailwind build command not removed from Dockerfile"
        )

    assert not DjangoProjectManager().has_dependency("django-tailwind-cli"), (
        "django-tailwind-cli dependency found after removal"
    )
