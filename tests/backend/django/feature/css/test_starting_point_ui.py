import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_backend

runner = CliRunner()


def test_starting_point_ui_install_and_remove(temp_dir):
    """
    Test Starting Point UI CSS framework installation and removal.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    # First install django-tailwind-cli as a prerequisite
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
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "starting-point-ui",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    # CSS should be in Tailwind source directory
    starting_point_ui_css_file = (
        backend_dir / "tailwind" / "src" / "css" / "starting-point-ui.min.css"
    )
    # JS should be in static directory
    starting_point_ui_js_file = (
        backend_dir / "static" / "js" / "starting-point-ui.min.js"
    )

    assert starting_point_ui_css_file.exists(), (
        "Starting Point UI CSS file not downloaded to Tailwind directory"
    )
    assert starting_point_ui_js_file.exists(), (
        "Starting Point UI JS file not downloaded to static directory"
    )

    assert starting_point_ui_css_file.stat().st_size > 0, (
        "Starting Point UI CSS file is empty"
    )
    assert starting_point_ui_js_file.stat().st_size > 0, (
        "Starting Point UI JS file is empty"
    )

    # Check input.css import
    input_css_path = backend_dir / "tailwind" / "src" / "css" / "input.css"
    assert input_css_path.exists(), "input.css not found"

    input_content = input_css_path.read_text()
    assert "starting-point-ui.min.css" in input_content, (
        "Starting Point UI import not added to input.css"
    )

    # Check base template for JS script
    base_template_path = backend_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()

    assert "starting-point-ui.min.js" in base_content, (
        "Starting Point UI JS script not added to base template"
    )

    assert 'type="module"' in base_content, (
        "Starting Point UI script missing type='module' attribute"
    )

    js_position = base_content.find("starting-point-ui.min.js")
    body_end = base_content.find("</body>")

    assert js_position > 0 and js_position < body_end, (
        "Starting Point UI JS not before closing body tag"
    )

    # Test removal
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "starting-point-ui",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not starting_point_ui_css_file.exists(), (
        "Starting Point UI CSS file not removed"
    )
    assert not starting_point_ui_js_file.exists(), (
        "Starting Point UI JS file not removed"
    )

    # Check input.css import removed
    input_content_after = input_css_path.read_text()
    assert "starting-point-ui.min.css" not in input_content_after, (
        "Starting Point UI import not removed from input.css"
    )

    # Check base template cleanup
    base_content_after = base_template_path.read_text()
    assert "starting-point-ui.min.js" not in base_content_after, (
        "Starting Point UI JS script not removed from base template"
    )


def test_starting_point_ui_install_idempotent(temp_dir):
    """
    Test that installing Starting Point UI multiple times doesn't create duplicate entries.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # First install django-tailwind-cli as a prerequisite
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
    assert result.exit_code == 0, f"Tailwind CLI install failed: {result.output}"

    for _ in range(2):
        result = runner.invoke(
            app,
            [
                "backend",
                "django",
                "feature",
                "css",
                "starting-point-ui",
                "install",
            ],
        )
        assert result.exit_code == 0, f"Install failed: {result.output}"

    # Check input.css for duplicate imports
    input_css_path = backend_dir / "tailwind" / "src" / "css" / "input.css"
    input_content = input_css_path.read_text()

    import_count = input_content.count("starting-point-ui.min.css")
    assert import_count == 1, (
        f"Expected 1 Starting Point UI import in input.css, found {import_count}"
    )

    # Check base template for duplicate scripts
    base_template_path = backend_dir / "templates" / "_base.html"
    base_content = base_template_path.read_text()

    js_count = base_content.count("starting-point-ui.min.js")
    assert js_count == 1, (
        f"Expected 1 Starting Point UI JS script in base template, found {js_count}"
    )


def test_starting_point_ui_remove_when_not_installed(temp_dir):
    """
    Test that removing Starting Point UI when not installed doesn't cause errors.
    """
    create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "starting-point-ui",
            "remove",
        ],
    )

    assert result.exit_code == 0, (
        f"Remove failed when nothing to remove: {result.output}"
    )


def test_starting_point_ui_requires_django_tailwind_cli(temp_dir):
    """
    Test that Starting Point UI install requires django-tailwind-cli.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Remove django-tailwind-cli from pyproject.toml to simulate missing dependency
    pyproject_path = backend_dir.parent / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        content = content.replace("django-tailwind-cli", "# django-tailwind-cli")
        pyproject_path.write_text(content)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "starting-point-ui",
            "install",
        ],
    )

    assert result.exit_code == 1, (
        "Install should fail when django-tailwind-cli is not installed"
    )
    assert "django-tailwind-cli" in result.output, (
        "Error message should mention django-tailwind-cli"
    )
