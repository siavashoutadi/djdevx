import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking._section import SectionTracking

runner = CliRunner()


def test_starting_point_ui_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["frameworks", "add", "starting_point_ui"])
    assert result.exit_code == 0, f"Install failed: {result.output}"

    sp_css_file = temp_dir / "tailwind" / "src" / "css" / "starting-point.css"
    sp_js_file = temp_dir / "static" / "js" / "vendor" / "starting-point.js"

    assert sp_css_file.exists(), "Starting Point CSS file not created"
    assert sp_js_file.exists(), "Starting Point JS file not created"
    assert sp_css_file.stat().st_size > 0, "Starting Point CSS file is empty"
    assert sp_js_file.stat().st_size > 0, "Starting Point JS file is empty"

    input_css_file = temp_dir / "tailwind" / "src" / "css" / "input.css"
    input_content = input_css_file.read_text()
    assert '@import "./starting-point.css";' in input_content, (
        "Starting Point import not added to input.css"
    )

    base_template_path = temp_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()
    assert "starting-point.js" in base_content, "Starting Point JS script not added"

    assert SectionTracking("frameworks").is_installed("starting-point-ui"), (
        "starting_point_ui should be tracked"
    )

    result = runner.invoke(app, ["frameworks", "remove", "starting-point-ui"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not sp_css_file.exists(), "Starting Point CSS file not removed"
    assert not sp_js_file.exists(), "Starting Point JS file not removed"

    input_content_after = input_css_file.read_text()
    assert '@import "./starting-point.css";' not in input_content_after, (
        "Starting Point import not removed"
    )

    base_content_after = base_template_path.read_text()
    assert "starting-point.js" not in base_content_after, (
        "Starting Point JS script not removed"
    )

    assert not SectionTracking("frameworks").is_installed("starting-point-ui"), (
        "tracking should be removed"
    )


def test_starting_point_ui_install_idempotent(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    for _ in range(2):
        result = runner.invoke(app, ["frameworks", "add", "starting_point_ui"])
        assert result.exit_code == 0

    input_css_file = temp_dir / "tailwind" / "src" / "css" / "input.css"
    input_content = input_css_file.read_text()
    assert input_content.count('@import "./starting-point.css";') == 1


def test_starting_point_ui_remove_when_not_installed(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    result = runner.invoke(app, ["frameworks", "remove", "starting-point-ui"])
    assert result.exit_code == 0
