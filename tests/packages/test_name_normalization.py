"""End-to-end test: CLI accepts underscore names and normalizes to hyphens."""

import os

from typer.testing import CliRunner

from djdevx.main import app
from djdevx.core.process import PixiRunner
from tests.test_helpers import create_test_django_project

runner = CliRunner()


def test_underscore_name_install_and_remove(temp_dir):
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["packages", "add", "django_htmx"])
    assert result.exit_code == 0, f"Install failed: {result.output}"
    assert PixiRunner().has_dependency("django-htmx")

    result = runner.invoke(app, ["packages", "remove", "django_htmx"])
    assert result.exit_code == 0, f"Remove failed: {result.output}"
    assert not PixiRunner().has_dependency("django-htmx")
