"""Tests for the create factory-boy CLI command."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.main import app
from tests.create.factory_fixtures import home_comment, home_post, users_user

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "factory"


def _scaffold_project(temp_dir) -> None:
    """Create a minimal djdevx project with a 'home' app (no pixi needed)."""
    (temp_dir / "djdevx.toml").write_text('[tool.djdevx]\nproject_name = "x"\n')
    (temp_dir / "home").mkdir(parents=True, exist_ok=True)
    (temp_dir / "users").mkdir(parents=True, exist_ok=True)


def _noop_format(*args, **kwargs):
    return None


def test_create_factory_noninteractive(temp_dir, monkeypatch):
    """--model generates <app>/factories.py matching the golden file."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.create.factory_boy.introspect.list_models",
            return_value=[home_post()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(app, ["create", "factory-boy", "--model", "home.Post"])

    assert result.exit_code == 0, f"Create factory failed: {result.output}"
    generated = temp_dir / "home" / "factories.py"
    assert generated.exists()
    assert generated.read_text() == (DATA_DIR / "home" / "factories.py").read_text()


def test_create_factory_multi_model_appends(temp_dir, monkeypatch):
    """Generating into an existing factories.py merges the new class."""
    _scaffold_project(temp_dir)
    target = temp_dir / "home" / "factories.py"
    target.write_text(
        "import factory\n"
        "from factory.django import DjangoModelFactory\n"
        "\n"
        "\n"
        "class PostFactory(DjangoModelFactory):\n"
        "    class Meta:\n"
        '        model = "home.Post"\n'
        "\n"
        '    title = factory.Faker("sentence")\n'
        '    author = factory.SubFactory("users.UserFactory")\n'
        "\n"
    )
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.create.factory_boy.introspect.list_models",
            return_value=[home_post(), home_comment(), users_user()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(
            app, ["create", "factory-boy", "--model", "home.Comment"]
        )

    assert result.exit_code == 0, f"Create factory failed: {result.output}"
    assert target.read_text() == (DATA_DIR / "append" / "factories.py").read_text()


def test_create_factory_updates_existing_with_new_fields(temp_dir, monkeypatch):
    """Re-running on a model that gained fields merges them into the factory."""
    _scaffold_project(temp_dir)
    target = temp_dir / "home" / "factories.py"
    target.write_text(
        "import factory\n"
        "from factory.django import DjangoModelFactory\n"
        "\n"
        "\n"
        "class PostFactory(DjangoModelFactory):\n"
        "    class Meta:\n"
        '        model = "home.Post"\n'
        '        django_get_or_create = ("slug",)\n'
        "\n"
        '    title = factory.Faker("sentence")\n'
        "\n"
    )
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.create.factory_boy.introspect.list_models",
            return_value=[home_post()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(app, ["create", "factory-boy", "--model", "home.Post"])

    assert result.exit_code == 0, f"Create factory failed: {result.output}"
    content = target.read_text()
    assert 'title = factory.Faker("sentence")' in content
    assert 'slug = factory.Faker("slug")' in content
    assert "def tags(self, create, extracted, **kwargs):" in content


def test_create_factory_interactive_prompt(temp_dir, monkeypatch):
    """Without --model the styled checkbox prompt collects the selection."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.create.factory_boy.introspect.list_models",
            return_value=[home_post()],
        ),
        patch("djdevx.create.factory_boy.prompts.checkbox", return_value=["home.Post"]),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(app, ["create", "factory-boy"])

    assert result.exit_code == 0, f"Prompted create failed: {result.output}"
    assert (temp_dir / "home" / "factories.py").exists()


def test_create_factory_unknown_model(temp_dir, monkeypatch):
    """An unknown model label must fail with a clean error."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    with (
        patch(
            "djdevx.create.factory_boy.introspect.list_models",
            return_value=[home_post()],
        ),
        patch("djdevx.create.factory_boy.format_files", side_effect=_noop_format),
    ):
        result = runner.invoke(app, ["create", "factory-boy", "--model", "nope.Bad"])

    assert result.exit_code != 0
    assert "Unknown model" in result.output


def test_create_factory_introspection_error(temp_dir, monkeypatch):
    """A failed introspection surfaces a friendly error and exits non-zero."""
    _scaffold_project(temp_dir)
    monkeypatch.chdir(temp_dir)

    from djdevx.create.factory_boy import introspect

    with patch(
        "djdevx.create.factory_boy.introspect.list_models",
        side_effect=introspect.IntrospectionError("Could not introspect"),
    ):
        result = runner.invoke(app, ["create", "factory-boy", "--model", "home.Post"])

    assert result.exit_code != 0
    assert "Could not introspect" in result.output
