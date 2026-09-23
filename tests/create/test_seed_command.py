"""Tests for the create seed-command CLI command."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.main import app
from tests.create.factory_fixtures import home_comment, home_post

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "seed_command"


def _scaffold_project(temp_dir) -> None:
    """Create a minimal djdevx project with a 'home' app (no pixi needed)."""
    (temp_dir / "djdevx.toml").write_text('[tool.djdevx]\nproject_name = "x"\n')
    (temp_dir / "home").mkdir(parents=True, exist_ok=True)
    (temp_dir / "users").mkdir(parents=True, exist_ok=True)


def _noop_format(*args, **kwargs):
    return None


def test_create_seed_command_noninteractive(temp_dir, monkeypatch):
    """--model generates the management command matching the golden file."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.utils.django.introspect.list_models",
            return_value=[home_post()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
        patch("djdevx.create.seed_command.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(app, ["create", "seed-command", "--model", "home.Post"])

    assert result.exit_code == 0, f"Create seed command failed: {result.output}"
    generated = temp_dir / "home" / "management" / "commands" / "home.py"
    assert generated.exists()
    assert generated.read_text() == (DATA_DIR / "home.py").read_text()
    assert (temp_dir / "home" / "factories.py").exists()


def test_create_seed_command_multi_model_matches_golden(temp_dir, monkeypatch):
    """Multiple models in one app land in a single command file."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.utils.django.introspect.list_models",
            return_value=[home_post(), home_comment()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
        patch("djdevx.create.seed_command.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(
            app,
            [
                "create",
                "seed-command",
                "--model",
                "home.Post",
                "--model",
                "home.Comment",
            ],
        )

    assert result.exit_code == 0, f"Create seed command failed: {result.output}"
    generated = temp_dir / "home" / "management" / "commands" / "home.py"
    assert generated.exists()
    assert generated.read_text() == (DATA_DIR / "home_both.py").read_text()


def test_create_seed_command_appends_missing_models(temp_dir, monkeypatch):
    """Re-running for a new model merges it into the existing command file."""
    _scaffold_project(temp_dir)
    target = temp_dir / "home" / "management" / "commands" / "home.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text((DATA_DIR / "home.py").read_text())
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.utils.django.introspect.list_models",
            return_value=[home_post(), home_comment()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
        patch("djdevx.create.seed_command.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(
            app, ["create", "seed-command", "--model", "home.Comment"]
        )

    assert result.exit_code == 0, f"Create seed command failed: {result.output}"
    content = target.read_text()
    assert "def seed_all" in content
    assert "def clean_all" in content
    assert "def seed_post" in content
    assert "def clean_post" in content
    assert "def seed_comment" in content
    assert "def clean_comment" in content
    assert "from home.models import Post, Comment" in content


def test_create_seed_command_idempotent_skips(temp_dir, monkeypatch):
    """Re-running for an already-present model skips without rewriting."""
    _scaffold_project(temp_dir)
    target = temp_dir / "home" / "management" / "commands" / "home.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text((DATA_DIR / "home.py").read_text())
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.utils.django.introspect.list_models",
            return_value=[home_post()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
        patch("djdevx.create.seed_command.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(app, ["create", "seed-command", "--model", "home.Post"])

    assert result.exit_code == 0
    assert "already present, skipped" in result.output
    assert target.read_text() == (DATA_DIR / "home.py").read_text()


def test_create_seed_command_interactive_prompt(temp_dir, monkeypatch):
    """Without --model the styled checkbox prompt collects the selection."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.utils.django.introspect.list_models",
            return_value=[home_post()],
        ),
        patch(
            "djdevx.utils.django.models.prompts.checkbox", return_value=["home.Post"]
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
        patch("djdevx.create.seed_command.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(app, ["create", "seed-command"])

    assert result.exit_code == 0, f"Prompted create failed: {result.output}"
    assert (temp_dir / "home" / "management" / "commands" / "home.py").exists()


def test_create_seed_command_unknown_model(temp_dir, monkeypatch):
    """An unknown model label must fail with a clean error."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.utils.django.introspect.list_models",
            return_value=[home_post()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
        patch("djdevx.create.seed_command.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(app, ["create", "seed-command", "--model", "nope.Bad"])

    assert result.exit_code != 0
    assert "Unknown model" in result.output


def test_create_seed_command_introspection_error(temp_dir, monkeypatch):
    """A failed introspection surfaces a friendly error and exits non-zero."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    from djdevx.utils.django import introspect

    with patch(
        "djdevx.utils.django.introspect.list_models",
        side_effect=introspect.IntrospectionError("Could not introspect"),
    ):
        result = runner.invoke(app, ["create", "seed-command", "--model", "home.Post"])

    assert result.exit_code != 0
    assert "Could not introspect" in result.output
