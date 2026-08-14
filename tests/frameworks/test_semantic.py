import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking._section import SectionTracking

runner = CliRunner()


def test_semantic_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["frameworks", "add", "semantic"])
    assert result.exit_code == 0, f"Install failed: {result.output}"

    semantic_css_file = temp_dir / "static" / "css" / "vendor" / "semantic.min.css"
    semantic_js_file = temp_dir / "static" / "js" / "vendor" / "semantic.min.js"

    assert semantic_css_file.exists(), "Semantic CSS file not downloaded"
    assert semantic_js_file.exists(), "Semantic JS file not downloaded"
    assert semantic_css_file.stat().st_size > 0, "Semantic CSS file is empty"
    assert semantic_js_file.stat().st_size > 0, "Semantic JS file is empty"

    base_template_path = temp_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()
    assert "semantic.min.css" in base_content, "Semantic CSS link not added"
    assert "semantic.min.js" in base_content, "Semantic JS script not added"

    assert SectionTracking("frameworks").is_installed("semantic"), (
        "semantic should be tracked"
    )

    result = runner.invoke(app, ["frameworks", "remove", "semantic"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not semantic_css_file.exists(), "Semantic CSS file not removed"
    assert not semantic_js_file.exists(), "Semantic JS file not removed"

    base_content_after = base_template_path.read_text()
    assert "semantic.min.css" not in base_content_after, "Semantic CSS link not removed"
    assert "semantic.min.js" not in base_content_after, "Semantic JS script not removed"

    assert not SectionTracking("frameworks").is_installed("semantic"), (
        "tracking should be removed"
    )


def test_semantic_install_idempotent(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    for _ in range(2):
        result = runner.invoke(app, ["frameworks", "add", "semantic"])
        assert result.exit_code == 0

    base_template_path = temp_dir / "templates" / "_base.html"
    base_content = base_template_path.read_text()
    assert base_content.count("semantic.min.css") == 1
    assert base_content.count("semantic.min.js") == 1


def test_semantic_remove_when_not_installed(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    result = runner.invoke(app, ["frameworks", "remove", "semantic"])
    assert result.exit_code == 0
