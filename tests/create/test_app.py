"""Tests for create app command."""

import os
from pathlib import Path
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
