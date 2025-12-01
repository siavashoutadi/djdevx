import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_backend

runner = CliRunner()


def test_frankenui_install_and_remove(temp_dir):
    """
    Test FrankenUI CSS framework installation and removal.
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
            "frankenui",
            "install",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    frankenui_css_file = backend_dir / "static" / "css" / "frankenui-core.min.css"
    frankenui_core_js_file = backend_dir / "static" / "js" / "frankenui-core.iife.js"
    frankenui_icon_js_file = backend_dir / "static" / "js" / "frankenui-icon.iife.js"

    assert frankenui_css_file.exists(), "FrankenUI CSS file not downloaded"
    assert frankenui_core_js_file.exists(), "FrankenUI Core JS file not downloaded"
    assert frankenui_icon_js_file.exists(), "FrankenUI Icon JS file not downloaded"

    assert frankenui_css_file.stat().st_size > 0, "FrankenUI CSS file is empty"
    assert frankenui_core_js_file.stat().st_size > 0, "FrankenUI Core JS file is empty"
    assert frankenui_icon_js_file.stat().st_size > 0, "FrankenUI Icon JS file is empty"

    base_template_path = backend_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()

    assert "frankenui-core.min.css" in base_content, (
        "FrankenUI CSS link not added to base template"
    )
    assert "frankenui-core.iife.js" in base_content, (
        "FrankenUI Core JS script not added to base template"
    )
    assert "frankenui-icon.iife.js" in base_content, (
        "FrankenUI Icon JS script not added to base template"
    )

    assert 'type="module"' in base_content, (
        "FrankenUI scripts missing type='module' attribute"
    )

    module_script_count = base_content.count('type="module"')
    assert module_script_count == 2, (
        f"Expected 2 module scripts, found {module_script_count}"
    )

    head_end = base_content.find("</head>")
    css_position = base_content.find("frankenui-core.min.css")
    core_js_position = base_content.find("frankenui-core.iife.js")
    icon_js_position = base_content.find("frankenui-icon.iife.js")

    assert css_position < head_end, "FrankenUI CSS not in head section"
    assert core_js_position < head_end, "FrankenUI Core JS not in head section"
    assert icon_js_position < head_end, "FrankenUI Icon JS not in head section"
    result = runner.invoke(
        app,
        [
            "backend",
            "django",
            "feature",
            "css",
            "frankenui",
            "remove",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not frankenui_css_file.exists(), "FrankenUI CSS file not removed"
    assert not frankenui_core_js_file.exists(), "FrankenUI Core JS file not removed"
    assert not frankenui_icon_js_file.exists(), "FrankenUI Icon JS file not removed"

    base_content_after = base_template_path.read_text()
    assert "frankenui-core.min.css" not in base_content_after, (
        "FrankenUI CSS link not removed from base template"
    )
    assert "frankenui-core.iife.js" not in base_content_after, (
        "FrankenUI Core JS script not removed from base template"
    )
    assert "frankenui-icon.iife.js" not in base_content_after, (
        "FrankenUI Icon JS script not removed from base template"
    )


def test_frankenui_install_idempotent(temp_dir):
    """
    Test that installing FrankenUI multiple times doesn't create duplicate entries.
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
                "frankenui",
                "install",
            ],
        )
        assert result.exit_code == 0, f"Install failed: {result.output}"

    base_template_path = backend_dir / "templates" / "_base.html"
    base_content = base_template_path.read_text()

    css_count = base_content.count("frankenui-core.min.css")
    core_js_count = base_content.count("frankenui-core.iife.js")
    icon_js_count = base_content.count("frankenui-icon.iife.js")

    assert css_count == 1, f"Expected 1 FrankenUI CSS link, found {css_count}"
    assert core_js_count == 1, (
        f"Expected 1 FrankenUI Core JS script, found {core_js_count}"
    )
    assert icon_js_count == 1, (
        f"Expected 1 FrankenUI Icon JS script, found {icon_js_count}"
    )


def test_frankenui_remove_when_not_installed(temp_dir):
    """
    Test that removing FrankenUI when not installed doesn't cause errors.
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
            "frankenui",
            "remove",
        ],
    )

    assert result.exit_code == 0, (
        f"Remove failed when nothing to remove: {result.output}"
    )
