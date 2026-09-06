"""Tests for create app command."""

import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.main import app
from tests.test_helpers import create_test_django_project

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "app"


def test_create_app(temp_dir):
    """
    Test that the CLI creates a new Django app successfully.
    """
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(
        app,
        [
            "create",
            "app",
            "--name",
            "home",
        ],
    )

    assert result.exit_code == 0, f"Create app failed: {result.output}"

    expected_files = [
        f.relative_to(DATA_DIR)
        for f in DATA_DIR.rglob("*")
        if f.is_file() and ".ruff_cache" not in f.parts
    ]

    for relative_path in expected_files:
        created_file = temp_dir / relative_path
        assert created_file.exists(), f"Missing file: {relative_path}"
        expected_content = (DATA_DIR / relative_path).read_text()
        actual_content = created_file.read_text()
        assert actual_content == expected_content, (
            f"Content mismatch in file: {relative_path}"
        )


def test_create_app_conflicting_name_fails_cleanly(temp_dir):
    """A conflicting app name must exit non-zero with Django's error, no hang."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    first = runner.invoke(app, ["create", "app", "--name", "home"])
    assert first.exit_code == 0, f"First create failed: {first.output}"

    second = runner.invoke(app, ["create", "app", "--name", "home"])
    assert second.exit_code != 0, (
        f"Conflicting app name unexpectedly succeeded: {second.output}"
    )
    assert "Could not create application 'home'" in second.output, (
        f"Missing clean failure message: {second.output}"
    )


def test_create_app_prompts_for_name(temp_dir):
    """Without --name, the styled questionary prompt collects the name."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    with patch("djdevx.create.prompts.text", return_value="prompted_app") as prompt:
        result = runner.invoke(app, ["create", "app"])

    assert result.exit_code == 0, f"Prompted create failed: {result.output}"
    prompt.assert_called_once()
    assert (temp_dir / "prompted_app" / "apps.py").exists(), (
        "prompted app was not created"
    )
