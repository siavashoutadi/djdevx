import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()


def test_drf_flex_fields_install_and_remove(temp_dir):
    """
    Test drf-flex-fields package installation and removal.
    Requires djangorestframework to be installed first.
    """

    create_test_django_project(temp_dir, runner)

    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "djangorestframework",
        ],
    )
    assert result.exit_code == 0, f"DRF install failed: {result.output}"

    result = runner.invoke(
        app,
        [
            "packages",
            "add",
            "drf_flex_fields",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    assert PixiRunner().has_dependency("drf-flex-fields"), (
        "drf-flex-fields dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "drf_flex_fields",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not PixiRunner().has_dependency("drf-flex-fields"), (
        "drf-flex-fields dependency found after removal"
    )
