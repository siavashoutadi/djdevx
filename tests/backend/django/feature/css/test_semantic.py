import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_backend

runner = CliRunner()


def test_semantic_install_and_remove(temp_dir):
    """
    Test Semantic UI CSS framework installation and removal.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "semantic",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    semantic_css_file = backend_dir / "static" / "css" / "semantic.min.css"
    semantic_js_file = backend_dir / "static" / "js" / "semantic.min.js"
    jquery_file = backend_dir / "static" / "js" / "jquery-3.1.1.min.js"

    assert semantic_css_file.exists(), "Semantic UI CSS file not downloaded"
    assert semantic_js_file.exists(), "Semantic UI JS file not downloaded"
    assert jquery_file.exists(), "jQuery file not downloaded"

    assert semantic_css_file.stat().st_size > 0, "Semantic UI CSS file is empty"
    assert semantic_js_file.stat().st_size > 0, "Semantic UI JS file is empty"
    assert jquery_file.stat().st_size > 0, "jQuery file is empty"

    base_template_path = backend_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()

    assert "semantic.min.css" in base_content, (
        "Semantic UI CSS link not added to base template"
    )
    assert "semantic.min.js" in base_content, (
        "Semantic UI JS script not added to base template"
    )
    assert "jquery-3.1.1.min.js" in base_content, (
        "jQuery script not added to base template"
    )

    css_position = base_content.find("semantic.min.css")
    jquery_position = base_content.find("jquery-3.1.1.min.js")
    semantic_js_position = base_content.find("semantic.min.js")
    head_end = base_content.find("</head>")
    body_end = base_content.find("</body>")

    assert css_position < head_end, "Semantic UI CSS not in head section"
    assert jquery_position > head_end and jquery_position < body_end, (
        "jQuery not before closing body tag"
    )
    assert semantic_js_position > head_end and semantic_js_position < body_end, (
        "Semantic UI JS not before closing body tag"
    )

    assert jquery_position < semantic_js_position, (
        "jQuery should be loaded before Semantic UI JS"
    )

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "semantic",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not semantic_css_file.exists(), "Semantic UI CSS file not removed"
    assert not semantic_js_file.exists(), "Semantic UI JS file not removed"
    assert not jquery_file.exists(), "jQuery file not removed"

    base_content_after = base_template_path.read_text()
    assert "semantic.min.css" not in base_content_after, (
        "Semantic UI CSS link not removed from base template"
    )
    assert "semantic.min.js" not in base_content_after, (
        "Semantic UI JS script not removed from base template"
    )
    assert "jquery-3.1.1.min.js" not in base_content_after, (
        "jQuery script not removed from base template"
    )


def test_semantic_install_idempotent(temp_dir):
    """
    Test that installing Semantic UI multiple times doesn't create duplicate entries.
    """
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    for _ in range(2):
        result = runner.invoke(
            app,
            [
                "backend",
                "django",
                "feature",
                "css",
                "semantic",
                "install",
            ],
        )
        assert result.exit_code == 0, f"Install failed: {result.output}"

    base_template_path = backend_dir / "templates" / "_base.html"
    base_content = base_template_path.read_text()

    css_count = base_content.count("semantic.min.css")
    semantic_js_count = base_content.count("semantic.min.js")
    jquery_count = base_content.count("jquery-3.1.1.min.js")

    assert css_count == 1, f"Expected 1 Semantic UI CSS link, found {css_count}"
    assert semantic_js_count == 1, (
        f"Expected 1 Semantic UI JS script, found {semantic_js_count}"
    )
    assert jquery_count == 1, f"Expected 1 jQuery script, found {jquery_count}"


def test_semantic_remove_when_not_installed(temp_dir):
    """
    Test that removing Semantic UI when not installed doesn't cause errors.
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
            "semantic",
            "remove",
        ],
    )

    assert result.exit_code == 0, (
        f"Remove failed when nothing to remove: {result.output}"
    )


def test_semantic_dependency_order(temp_dir):
    """
    Test that jQuery is loaded before Semantic UI JS (proper dependency order).
    """
    backend_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "semantic",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    base_template_path = backend_dir / "templates" / "_base.html"
    base_content = base_template_path.read_text()

    jquery_pos = base_content.find("jquery-3.1.1.min.js")
    semantic_js_pos = base_content.find("semantic.min.js")

    assert jquery_pos < semantic_js_pos, "jQuery must be loaded before Semantic UI JS"

    head_end = base_content.find("</head>")
    body_end = base_content.find("</body>")

    assert jquery_pos > head_end, "jQuery script should be in body section"
    assert semantic_js_pos > head_end, "Semantic UI JS script should be in body section"
    assert jquery_pos < body_end, "jQuery script should be before closing body tag"
    assert semantic_js_pos < body_end, (
        "Semantic UI JS script should be before closing body tag"
    )
