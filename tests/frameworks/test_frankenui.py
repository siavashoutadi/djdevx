import os
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_project
from djdevx.utils.tracking import ProjectTracking, Section

runner = CliRunner()

PLACEHOLDER = "/* placeholder */\n"

VENDOR_ASSETS = [
    ("static/css/vendor/franken-core.css", "link"),
    ("static/css/vendor/franken-utilities.css", "link"),
    ("static/js/vendor/franken-core.js", "script"),
    ("static/js/vendor/franken-icon.js", "script"),
]


def _assert_real_downloads(temp_dir):
    for rel_path, _ in VENDOR_ASSETS:
        path = temp_dir / rel_path
        assert path.exists(), f"{rel_path} not downloaded"
        assert path.stat().st_size > 0, f"{rel_path} is empty"
        assert path.read_text() != PLACEHOLDER, (
            f"{rel_path} is a download-failure placeholder"
        )


def test_frankenui_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["frameworks", "add", "frankenui"])
    assert result.exit_code == 0, f"Install failed: {result.output}"

    _assert_real_downloads(temp_dir)

    base_template_path = temp_dir / "templates" / "_base.html"
    assert base_template_path.exists(), "Base template not found"

    base_content = base_template_path.read_text()
    for rel_path, _ in VENDOR_ASSETS:
        filename = os.path.basename(rel_path)
        assert filename in base_content, f"{filename} tag not added"
    assert 'type="module"' in base_content, "type=module not set on script"

    assert ProjectTracking().is_installed(Section.FRAMEWORKS, "frankenui"), (
        "frankenui should be tracked"
    )

    result = runner.invoke(app, ["frameworks", "remove", "frankenui"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"

    for rel_path, _ in VENDOR_ASSETS:
        assert not (temp_dir / rel_path).exists(), f"{rel_path} not removed"

    base_content_after = base_template_path.read_text()
    for rel_path, _ in VENDOR_ASSETS:
        filename = os.path.basename(rel_path)
        assert filename not in base_content_after, f"{filename} tag not removed"

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
    for rel_path, _ in VENDOR_ASSETS:
        filename = os.path.basename(rel_path)
        assert base_content.count(filename) == 1, f"expected exactly one {filename} tag"


def test_frankenui_remove_when_not_installed(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    result = runner.invoke(app, ["frameworks", "remove", "frankenui"])
    assert result.exit_code == 0
