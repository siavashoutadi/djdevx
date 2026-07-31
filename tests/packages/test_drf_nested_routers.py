import os
from typer.testing import CliRunner
from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()


def test_drf_nested_routers_install_and_remove(temp_dir):
    """
    Test drf-nested-routers package installation and removal.
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
            "drf_nested_routers",
        ],
    )

    assert result.exit_code == 0, f"Install failed: {result.output}"

    assert PixiRunner().has_dependency("drf-nested-routers"), (
        "drf-nested-routers dependency not found after installation"
    )

    os.chdir(temp_dir)
    result = runner.invoke(
        app,
        [
            "packages",
            "remove",
            "drf_nested_routers",
        ],
    )

    assert result.exit_code == 0, f"Remove failed: {result.output}"

    assert not PixiRunner().has_dependency("drf-nested-routers"), (
        "drf-nested-routers dependency found after removal"
    )
