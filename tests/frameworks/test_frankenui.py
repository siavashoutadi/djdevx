import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking import ProjectTracking, Section

runner = CliRunner()


def test_frankenui_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["frameworks", "add", "frankenui"])
    assert result.exit_code == 0, f"Install failed: {result.output}"

    franken_css_file = temp_dir / "static" / "css" / "vendor" / "franken.css"
    franken_js_file = temp_dir / "static" / "js" / "vendor" / "franken.js"

    assert franken_css_file.exists(), "Franken CSS file not downloaded"
    assert franken_js_file.exists(), "Franken JS file not downloaded"
    assert franken_css_file.stat().st_size > 0, "Franken CSS file is empty"
    assert franken_js_file.stat().st_size > 0, "Franken JS file is empty"

    base_template_path = temp_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()
    assert "franken.css" in base_content, "Franken CSS link not added"
    assert "franken.js" in base_content, "Franken JS script not added"
    assert 'type="module"' in base_content, "type=module not set on script"

    assert ProjectTracking().is_installed(Section.FRAMEWORKS, "frankenui"), (
        "frankenui should be tracked"
    )

    result = runner.invoke(app, ["frameworks", "remove", "frankenui"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not franken_css_file.exists(), "Franken CSS file not removed"
    assert not franken_js_file.exists(), "Franken JS file not removed"

    base_content_after = base_template_path.read_text()
    assert "franken.css" not in base_content_after, "Franken CSS link not removed"
    assert "franken.js" not in base_content_after, "Franken JS script not removed"

    assert not ProjectTracking().is_installed(Section.FRAMEWORKS, "frankenui"), (
        "tracking should be removed"
    )


def test_frankenui_install_idempotent(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    for _ in range(2):
        result = runner.invoke(app, ["frameworks", "add", "frankenui"])
        assert result.exit_code == 0, f"Install failed: {result.output}"

    base_template_path = temp_dir / "templates" / "_base.html"
    base_content = base_template_path.read_text()
    assert base_content.count("franken.css") == 1
    assert base_content.count("franken.js") == 1


def test_frankenui_remove_when_not_installed(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    result = runner.invoke(app, ["frameworks", "remove", "frankenui"])
    assert result.exit_code == 0
