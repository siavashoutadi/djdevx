import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_backend

runner = CliRunner()


def test_bootstrap_install_and_remove(temp_dir):
    """
    Test Bootstrap CSS framework installation and removal.
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
            "bootstrap",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    bootstrap_css_file = backend_dir / "static" / "css" / "bootstrap.min.css"
    bootstrap_js_file = backend_dir / "static" / "js" / "bootstrap.bundle.min.js"

    assert bootstrap_css_file.exists(), "Bootstrap CSS file not downloaded"
    assert bootstrap_js_file.exists(), "Bootstrap JS file not downloaded"

    assert bootstrap_css_file.stat().st_size > 0, "Bootstrap CSS file is empty"
    assert bootstrap_js_file.stat().st_size > 0, "Bootstrap JS file is empty"

    base_template_path = backend_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()

    assert "bootstrap.min.css" in base_content, (
        "Bootstrap CSS link not added to base template"
    )
    assert "bootstrap.bundle.min.js" in base_content, (
        "Bootstrap JS script not added to base template"
    )

    css_position = base_content.find("bootstrap.min.css")
    js_position = base_content.find("bootstrap.bundle.min.js")
    head_end = base_content.find("</head>")
    body_end = base_content.find("</body>")

    assert css_position < head_end, "Bootstrap CSS not in head section"
    assert js_position > head_end and js_position < body_end, (
        "Bootstrap JS not before closing body tag"
    )

    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "bootstrap",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not bootstrap_css_file.exists(), "Bootstrap CSS file not removed"
    assert not bootstrap_js_file.exists(), "Bootstrap JS file not removed"

    base_content_after = base_template_path.read_text()
    assert "bootstrap.min.css" not in base_content_after, (
        "Bootstrap CSS link not removed from base template"
    )
    assert "bootstrap.bundle.min.js" not in base_content_after, (
        "Bootstrap JS script not removed from base template"
    )


def test_bootstrap_install_idempotent(temp_dir):
    """
    Test that installing Bootstrap multiple times doesn't create duplicate entries.
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
                "bootstrap",
                "install",
            ],
        )
        assert result.exit_code == 0, f"Install failed: {result.output}"

    base_template_path = backend_dir / "templates" / "_base.html"
    base_content = base_template_path.read_text()

    css_count = base_content.count("bootstrap.min.css")
    js_count = base_content.count("bootstrap.bundle.min.js")

    assert css_count == 1, f"Expected 1 Bootstrap CSS link, found {css_count}"
    assert js_count == 1, f"Expected 1 Bootstrap JS script, found {js_count}"


def test_bootstrap_remove_when_not_installed(temp_dir):
    """
    Test that removing Bootstrap when not installed doesn't cause errors.
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
            "bootstrap",
            "remove",
        ],
    )

    assert result.exit_code == 0, (
        f"Remove failed when nothing to remove: {result.output}"
    )
