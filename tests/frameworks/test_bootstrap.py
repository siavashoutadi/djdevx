import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking import ProjectTracking, Section

runner = CliRunner()


def test_bootstrap_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["frameworks", "add", "bootstrap"])
    assert result.exit_code == 0, f"Install failed: {result.output}"

    bootstrap_css_file = temp_dir / "static" / "css" / "vendor" / "bootstrap.min.css"
    bootstrap_js_file = (
        temp_dir / "static" / "js" / "vendor" / "bootstrap.bundle.min.js"
    )

    assert bootstrap_css_file.exists(), "Bootstrap CSS file not downloaded"
    assert bootstrap_js_file.exists(), "Bootstrap JS file not downloaded"
    assert bootstrap_css_file.stat().st_size > 0, "Bootstrap CSS file is empty"
    assert bootstrap_js_file.stat().st_size > 0, "Bootstrap JS file is empty"

    base_template_path = temp_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()
    assert "bootstrap.min.css" in base_content, "Bootstrap CSS link not added"
    assert "bootstrap.bundle.min.js" in base_content, "Bootstrap JS script not added"

    assert ProjectTracking().is_installed(Section.FRAMEWORKS, "bootstrap"), (
        "bootstrap should be tracked after install"
    )

    css_position = base_content.find("bootstrap.min.css")
    js_position = base_content.find("bootstrap.bundle.min.js")
    head_end = base_content.find("</head>")
    body_end = base_content.find("</body>")
    assert css_position < head_end, "Bootstrap CSS not in head section"
    assert js_position > head_end and js_position < body_end, (
        "Bootstrap JS not before closing body tag"
    )

    result = runner.invoke(app, ["frameworks", "remove", "bootstrap"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not bootstrap_css_file.exists(), "Bootstrap CSS file not removed"
    assert not bootstrap_js_file.exists(), "Bootstrap JS file not removed"

    base_content_after = base_template_path.read_text()
    assert "bootstrap.min.css" not in base_content_after, (
        "Bootstrap CSS link not removed"
    )
    assert "bootstrap.bundle.min.js" not in base_content_after, (
        "Bootstrap JS script not removed"
    )

    assert not ProjectTracking().is_installed(Section.FRAMEWORKS, "bootstrap"), (
        "bootstrap tracking should be removed"
    )


def test_bootstrap_install_idempotent(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    for _ in range(2):
        result = runner.invoke(app, ["frameworks", "add", "bootstrap"])
        assert result.exit_code == 0, f"Install failed: {result.output}"

    base_template_path = temp_dir / "templates" / "_base.html"
    base_content = base_template_path.read_text()

    css_count = base_content.count("bootstrap.min.css")
    js_count = base_content.count("bootstrap.bundle.min.js")
    assert css_count == 1, f"Expected 1 Bootstrap CSS link, found {css_count}"
    assert js_count == 1, f"Expected 1 Bootstrap JS script, found {js_count}"


def test_bootstrap_remove_when_not_installed(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    result = runner.invoke(app, ["frameworks", "remove", "bootstrap"])
    assert result.exit_code == 0
