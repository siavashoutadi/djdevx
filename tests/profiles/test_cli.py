"""CLI integration tests for `ddx profiles` and profile management."""

from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.main import app
from typer.main import get_command

runner = CliRunner()


class TestProfileAutocompletion:
    def test_profile_option_completes_builtin_names(self):
        new_group = get_command(app).commands["new"]
        profile_param = next(p for p in new_group.params if p.name == "profile")

        ctx = new_group.make_context("", [])
        assert [str(i.value) for i in profile_param.shell_complete(ctx, "multi")] == [
            "multi-page"
        ]
        assert [str(i.value) for i in profile_param.shell_complete(ctx, "")] == [
            "multi-page"
        ]
        assert profile_param.shell_complete(ctx, "api") == []


class TestProfilesSubcommand:
    def test_list_builtin(self):
        result = runner.invoke(app, ["profiles", "list"])
        assert result.exit_code == 0
        assert "multi-page" in result.stdout

    def test_create_from_project(self, temp_dir, monkeypatch):
        (temp_dir / "djdevx.toml").write_text(
            "project_name = 'x'\n[packages]\n[packages.whitenoise]\ninstalled = true\n"
        )
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(
            app,
            [
                "profiles",
                "create",
                "--from-project",
                "--output",
                str(temp_dir / "p.toml"),
            ],
        )
        assert result.exit_code == 0, result.stdout
        out = temp_dir / "p.toml"
        assert out.exists()
        assert "whitenoise" in out.read_text()

    def test_create_from_project_outside_project_fails(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["profiles", "create", "--from-project"])
        assert result.exit_code == 1
        assert "djdevx.toml" in result.stdout

    def test_create_help(self):
        result = runner.invoke(app, ["profiles", "create", "--help"])
        assert result.exit_code == 0
        assert "--from-project" in result.stdout
        assert "--interactive" in result.stdout
        assert "--output" in result.stdout

    def test_cancel_confirm_aborts_without_file(self, temp_dir, monkeypatch):
        (temp_dir / "djdevx.toml").write_text(
            "project_name = 'x'\n[packages]\n[packages.whitenoise]\ninstalled = true\n"
        )
        monkeypatch.chdir(temp_dir)
        with patch("djdevx.profiles.cli.prompts.confirm", return_value=None):
            result = runner.invoke(
                app, ["profiles", "create", "--output", str(temp_dir / "p.toml")]
            )
        assert result.exit_code == 1
        assert not (temp_dir / "p.toml").exists()


class TestNewWithProfile:
    def test_profile_routed_to_callback(self, temp_dir):
        profile_path = temp_dir / "p.toml"
        profile_path.write_text("[packages]\nwhitenoise = {}\n")

        with (
            patch("djdevx.new.requirement_check"),
            patch("djdevx.new._install_profile_items") as install_mock,
            patch("djdevx.new._init_git_repository"),
            patch("djdevx.new._commit_initial_git"),
            patch("djdevx.new._is_git_repository", return_value=True),
        ):
            result = runner.invoke(
                app,
                [
                    "new",
                    "--project-name",
                    "proj",
                    "--project-description",
                    "desc",
                    "--project-directory",
                    str(temp_dir / "proj"),
                    "--python-version",
                    "3.14",
                    "--no-git-init",
                    "--profile",
                    str(profile_path),
                ],
            )

        assert result.exit_code == 0, result.stdout
        install_mock.assert_called_once()
        args = install_mock.call_args
        profile_model = args[0][1]
        assert "whitenoise" in profile_model.packages

    def test_builtin_profile_routing(self, temp_dir):
        with (
            patch("djdevx.new.requirement_check"),
            patch("djdevx.new._install_profile_items") as install_mock,
            patch("djdevx.new._init_git_repository"),
            patch("djdevx.new._commit_initial_git"),
            patch("djdevx.new._is_git_repository", return_value=True),
        ):
            result = runner.invoke(
                app,
                [
                    "new",
                    "--project-name",
                    "proj",
                    "--project-description",
                    "desc",
                    "--project-directory",
                    str(temp_dir / "proj"),
                    "--python-version",
                    "3.14",
                    "--no-git-init",
                    "--profile",
                    "multi-page",
                ],
            )

        assert result.exit_code == 0, result.stdout
        install_mock.assert_called_once()
        args = install_mock.call_args
        profile_model = args[0][1]
        assert "django-htmx" in profile_model.packages

    def test_unknown_profile_name_fails_cleanly(self):
        with patch("djdevx.new.requirement_check") as req:
            result = runner.invoke(app, ["new", "--profile", "does-not-exist"])

        assert result.exit_code == 1
        assert "Unknown built-in profile 'does-not-exist'" in result.stdout
        assert "multi-page" in result.stdout
        req.assert_not_called()

    def test_missing_profile_file_fails_cleanly(self):
        result = runner.invoke(app, ["new", "--profile", "./nope.toml"])

        assert result.exit_code == 1
        assert "Profile file not found: ./nope.toml" in result.stdout

    def test_missing_answers_file_fails_before_scaffold(self, temp_dir):
        profile_path = temp_dir / "p.toml"
        profile_path.write_text("[packages]\nwhitenoise = {}\n")

        with (
            patch("djdevx.new.requirement_check") as req,
            patch("djdevx.new._install_profile_items") as install_mock,
        ):
            result = runner.invoke(
                app,
                [
                    "new",
                    "--profile",
                    str(profile_path),
                    "--answers",
                    str(temp_dir / "missing-answers.toml"),
                ],
            )

        assert result.exit_code == 1
        assert "Profile file not found" in result.stdout
        req.assert_not_called()
        install_mock.assert_not_called()

    def test_answers_file_passed_to_installer(self, temp_dir):
        profile_path = temp_dir / "p.toml"
        profile_path.write_text("[features]\npwa = {}\n")
        answers_path = temp_dir / "a.toml"
        answers_path.write_text("[features.pwa]\napp_name = 'X'\n")

        with (
            patch("djdevx.new.requirement_check"),
            patch("djdevx.new._install_profile_items") as install_mock,
            patch("djdevx.new._init_git_repository"),
            patch("djdevx.new._commit_initial_git"),
            patch("djdevx.new._is_git_repository", return_value=True),
        ):
            result = runner.invoke(
                app,
                [
                    "new",
                    "--project-name",
                    "proj",
                    "--project-description",
                    "desc",
                    "--project-directory",
                    str(temp_dir / "proj"),
                    "--python-version",
                    "3.14",
                    "--no-git-init",
                    "--profile",
                    str(profile_path),
                    "--answers",
                    str(answers_path),
                ],
            )

        assert result.exit_code == 0, result.stdout
        install_mock.assert_called_once()
        args = install_mock.call_args
        answers_model = args[0][2]
        assert answers_model.features["pwa"]["app_name"] == "X"
