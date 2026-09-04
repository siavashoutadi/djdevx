import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from djdevx.core.process import PixiRunner


# ---------------------------------------------------------------------------
# _extract_package_name (static method, no mocking needed)
# ---------------------------------------------------------------------------

extract_cases = [
    ("package", "package"),
    ("zope.interface", "zope.interface"),
    ("my-package", "my-package"),
    ("my_package", "my_package"),
    ("2to3", "2to3"),
    ("A.B-C_D", "A.B-C_D"),
    ("package[extra]", "package"),
    ("package[extra1,extra2]", "package"),
    ("package[extra1, extra2]", "package"),
    ("package[]", "package"),
    ("package==1.0", "package"),
    ("package == 1.0", "package"),
    ("package>=1.0", "package"),
    ("package<=1.0", "package"),
    ("package~=1.4.2", "package"),
    ("package!=1.0", "package"),
    ("package>1.0", "package"),
    ("package<1.0", "package"),
    ("package===1.0", "package"),
    ("package>=1.0,<2.0", "package"),
    ("package >= 1.0, < 2.0", "package"),
    ("package; python_version >= '3.6'", "package"),
    ("package; sys_platform == 'win32'", "package"),
    ("package>=1.0; python_version >= '3.6'", "package"),
    ("package @ https://example.com/pkg.zip", "package"),
    ("package@https://example.com/pkg.zip", "package"),
    ("package @ git+https://github.com/pypa/pip.git", "package"),
    ("package @ git+ssh://git@example.com/MyProject", "package"),
    ("package[security]>=1.0", "package"),
    ("package[security]>=1.0; python_version >= '3.6'", "package"),
    ("package[extra] @ https://example.com/pkg.zip", "package"),
    ("  package>=1.0  ", "package"),
    ("package (>=1.0, <2.0)", "package"),
    ("package=1.0", "package"),
    ("-e /path/to/project", "-e"),
    ("-e /path/to/project[extra]", "-e"),
    ("git+https://repo.git", "git+https://repo.git"),
]


@pytest.mark.parametrize("spec,expected", extract_cases)
def test_extract_package_name(spec: str, expected: str) -> None:
    assert PixiRunner._extract_package_name(spec) == expected


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestInit:
    def test_explicit_project_root(self):
        root = Path("/custom/project")
        runner = PixiRunner(project_root=root)
        assert runner.project_root == root

    def test_falls_back_to_project_structure(self):
        mock_structure = MagicMock()
        mock_structure.root = Path("/auto")
        with patch(
            "djdevx.core.process.ProjectStructure",
            return_value=mock_structure,
        ):
            runner = PixiRunner()
            assert runner.project_root == Path("/auto")


# ---------------------------------------------------------------------------
# run_manage_command
# ---------------------------------------------------------------------------


class TestRunManageCommand:
    def test_delegates_to_run_pixi_command(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.run_manage_command("startapp", "myapp")
            mock_run.assert_called_once_with(
                "run", "python", "manage.py", "startapp", "myapp", check=True
            )


# ---------------------------------------------------------------------------
# run_pixi_command
# ---------------------------------------------------------------------------


class TestRunPixiCommand:
    def test_passes_correct_args_to_subprocess(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch("subprocess.run") as mock_sub_run:
            runner.run_pixi_command("add", "numpy")
            mock_sub_run.assert_called_once()
            call_args = mock_sub_run.call_args[0][0]
            assert call_args == ["pixi", "add", "numpy"]
            assert mock_sub_run.call_args[1]["cwd"] == Path("/tmp")
            assert mock_sub_run.call_args[1]["check"] is True

    def test_check_false(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch("subprocess.run") as mock_sub_run:
            runner.run_pixi_command("search", "pkg", check=False)
            assert mock_sub_run.call_args[1]["check"] is False

    def test_capture_output_default(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch("subprocess.run") as mock_sub_run:
            runner.run_pixi_command("add", "numpy")
            assert mock_sub_run.call_args[1]["capture_output"] is True

    def test_verbose_disables_capture_output(self):
        runner = PixiRunner(project_root=Path("/tmp"), verbose=True)
        with patch("subprocess.run") as mock_sub_run:
            runner.run_pixi_command("add", "numpy")
            assert "capture_output" not in mock_sub_run.call_args[1]


# ---------------------------------------------------------------------------
# run_interactive
# ---------------------------------------------------------------------------


class TestRunInteractive:
    def test_builds_pixi_command_with_project_root(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch("subprocess.run") as mock_sub_run:
            runner.run_interactive("run", "python", "manage.py", "runserver")
            cmd = mock_sub_run.call_args[0][0]
            assert cmd == ["pixi", "run", "python", "manage.py", "runserver"]
            assert mock_sub_run.call_args[1]["cwd"] == Path("/tmp")

    def test_inherits_stdio(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch("subprocess.run") as mock_sub_run:
            runner.run_interactive("run", "python", "manage.py", "runserver")
            assert "capture_output" not in mock_sub_run.call_args[1]

    def test_returns_completed_process(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        expected = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=expected):
            result = runner.run_interactive("run", "python", "manage.py", "runserver")
            assert result is expected


# ---------------------------------------------------------------------------
# add_conda_package / add_pypi_package / add_package
# ---------------------------------------------------------------------------


class TestAddCondaPackage:
    def test_direct(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.add_conda_package("numpy")
            mock_run.assert_called_once_with("add", "numpy")

    def test_with_feature(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.add_conda_package("numpy", feature="dev")
            mock_run.assert_called_once_with("add", "numpy", "--feature", "dev")


class TestAddPypiPackage:
    def test_direct(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.add_pypi_package("django-typer")
            mock_run.assert_called_once_with("add", "--pypi", "django-typer")

    def test_with_feature(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.add_pypi_package("django-typer", pixi_feature="dev")
            mock_run.assert_called_once_with(
                "add", "--pypi", "django-typer", "--feature", "dev"
            )


class TestAddPackage:
    def test_delegates_to_add_conda_package(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "add_conda_package") as mock_conda:
            runner.add_package("numpy")
            mock_conda.assert_called_once_with("numpy", None)

    def test_with_feature(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "add_conda_package") as mock_conda:
            runner.add_package("ruff", feature="dev")
            mock_conda.assert_called_once_with("ruff", "dev")


# ---------------------------------------------------------------------------
# remove_conda_package / remove_pypi_package / remove_package
# ---------------------------------------------------------------------------


class TestRemoveCondaPackage:
    def test_succeeds(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            result = runner.remove_conda_package("numpy")
            assert result is mock_run.return_value
            mock_run.assert_called_once_with("remove", "numpy")

    def test_idempotent_on_failure(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(
            runner,
            "run_pixi_command",
            side_effect=subprocess.CalledProcessError(1, "pixi"),
        ):
            assert runner.remove_conda_package("nope") is None

    def test_with_feature(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.remove_conda_package("numpy", pixi_feature="dev")
            mock_run.assert_called_once_with("remove", "numpy", "--feature", "dev")


class TestRemovePypiPackage:
    def test_succeeds(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            result = runner.remove_pypi_package("django-typer")
            assert result is mock_run.return_value
            mock_run.assert_called_once_with("remove", "--pypi", "django-typer")

    def test_idempotent_on_failure(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(
            runner,
            "run_pixi_command",
            side_effect=subprocess.CalledProcessError(1, "pixi"),
        ):
            assert runner.remove_pypi_package("nope") is None


class TestRemovePackage:
    def test_delegates_to_remove_conda_package(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "remove_conda_package") as mock_remove:
            runner.remove_package("numpy")
            mock_remove.assert_called_once_with("numpy", None)

    def test_with_feature(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "remove_conda_package") as mock_remove:
            runner.remove_package("numpy", feature="dev")
            mock_remove.assert_called_once_with("numpy", "dev")


# ---------------------------------------------------------------------------
# list_dependencies
# ---------------------------------------------------------------------------


class TestListDependencies:
    def test_parses_normal_output(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        stdout = (
            "Package           Version     Build               Kind   Source\n"
            "django            5.0.1       pyhcb2e6_1          conda  django-5.0.1.conda\n"
            "django-typer      1.2.0       pypi                pypi   django_typer-1.2.0.whl\n"
        )
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=stdout)
            result = runner.list_dependencies()
            assert result == ["django", "django-typer"]

    def test_empty_output(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            assert runner.list_dependencies() == []

    def test_with_environment(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            runner.list_dependencies(environment="dev")
            mock_run.assert_called_once()
            args = mock_run.call_args[0]
            assert "--environment" in args
            assert args[-1] == "dev"

    def test_respects_explicit_flag(self):
        runner = PixiRunner(project_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            runner.list_dependencies()
            args = mock_run.call_args[0]
            assert "--explicit" in args
