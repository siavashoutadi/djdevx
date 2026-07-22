import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from djdevx.utils.django.pixi_runner import PixiRunner


# ---------------------------------------------------------------------------
# _extract_package_name (static method, no mocking needed)
# ---------------------------------------------------------------------------

extract_cases = [
    # bare names
    ("package", "package"),
    ("zope.interface", "zope.interface"),
    ("my-package", "my-package"),
    ("my_package", "my_package"),
    ("2to3", "2to3"),
    ("A.B-C_D", "A.B-C_D"),
    # extras
    ("package[extra]", "package"),
    ("package[extra1,extra2]", "package"),
    ("package[extra1, extra2]", "package"),
    ("package[]", "package"),
    # version operators – single
    ("package==1.0", "package"),
    ("package == 1.0", "package"),
    ("package>=1.0", "package"),
    ("package<=1.0", "package"),
    ("package~=1.4.2", "package"),
    ("package!=1.0", "package"),
    ("package>1.0", "package"),
    ("package<1.0", "package"),
    ("package===1.0", "package"),
    # multi-clause version
    ("package>=1.0,<2.0", "package"),
    ("package >= 1.0, < 2.0", "package"),
    # markers
    ("package; python_version >= '3.6'", "package"),
    ("package; sys_platform == 'win32'", "package"),
    # version + marker
    ("package>=1.0; python_version >= '3.6'", "package"),
    # URL / direct reference
    ("package @ https://example.com/pkg.zip", "package"),
    ("package@https://example.com/pkg.zip", "package"),
    ("package @ git+https://github.com/pypa/pip.git", "package"),
    ("package @ git+ssh://git@example.com/MyProject", "package"),
    # combined
    ("package[security]>=1.0", "package"),
    ("package[security]>=1.0; python_version >= '3.6'", "package"),
    ("package[extra] @ https://example.com/pkg.zip", "package"),
    # edge: whitespace
    ("  package>=1.0  ", "package"),
    # edge: parenthesized (PEP 345 legacy)
    ("package (>=1.0, <2.0)", "package"),
    # edge: conda single =
    ("package=1.0", "package"),
    # edge: pip editable (-e)
    ("-e /path/to/project", "-e"),
    ("-e /path/to/project[extra]", "-e"),
    # edge: bare VCS URL (no @)
    ("git+https://repo.git", "git+https://repo.git"),
]


@pytest.mark.parametrize("spec,expected", extract_cases)
def test_extract_package_name(spec: str, expected: str) -> None:
    assert PixiRunner._extract_package_name(spec) == expected


# ---------------------------------------------------------------------------
# _exists_in_conda
# ---------------------------------------------------------------------------


class TestExistsInConda:
    def test_found(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_result = MagicMock(returncode=0)
            mock_run.return_value = mock_result
            assert runner._exists_in_conda("django") is True
            mock_run.assert_called_once()
            args = mock_run.call_args[0]
            assert args[0] == "search"

    def test_not_found(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert runner._exists_in_conda("nonexistent-pkg") is False

    def test_strips_version_specifier(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            runner._exists_in_conda("django~=5.0")
            name_arg = mock_run.call_args[0][3]
            assert name_arg == "django"


# ---------------------------------------------------------------------------
# _find_installed_source
# ---------------------------------------------------------------------------


class TestFindInstalledSource:
    def test_conda_package(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps([{"name": "numpy", "kind": "conda"}]),
            )
            assert runner._find_installed_source("numpy") == "conda"

    def test_pypi_package(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps([{"name": "django-typer", "kind": "pypi"}]),
            )
            assert runner._find_installed_source("django-typer") == "pypi"

    def test_not_installed_empty_array(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="[]")
            assert runner._find_installed_source("missing") is None

    def test_not_installed_non_zero(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert runner._find_installed_source("missing") is None

    def test_json_decode_error(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="not json")
            assert runner._find_installed_source("pkg") is None

    def test_strips_version_specifier(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps([{"name": "django", "kind": "conda"}]),
            )
            result = runner._find_installed_source("django~=5.0")
            assert result == "conda"

    def test_name_normalization_hyphens_to_underscores(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps([{"name": "django_typer", "kind": "pypi"}]),
            )
            assert runner._find_installed_source("django-typer") == "pypi"

    def test_name_normalization_underscores_to_hyphens(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps([{"name": "django-typer", "kind": "pypi"}]),
            )
            assert runner._find_installed_source("django_typer") == "pypi"

    def test_name_normalization_dots(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps([{"name": "zope.interface", "kind": "conda"}]),
            )
            assert runner._find_installed_source("zope-interface") == "conda"

    def test_exact_match_among_many(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps(
                    [
                        {"name": "django", "kind": "conda"},
                        {"name": "djangorestframework", "kind": "conda"},
                    ]
                ),
            )
            assert runner._find_installed_source("django") == "conda"

    def test_with_environment(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps([{"name": "ruff", "kind": "conda"}]),
            )
            result = runner._find_installed_source("ruff", environment="dev")
            assert result == "conda"
            assert "--environment" in mock_run.call_args[0]
            assert mock_run.call_args[0][-1] == "dev"


# ---------------------------------------------------------------------------
# add_package / add_conda_package / add_pypi_package
# ---------------------------------------------------------------------------


class TestAddPackage:
    def test_conda_found_routes_to_add_conda(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_exists_in_conda", return_value=True),
            patch.object(runner, "add_conda_package") as mock_conda,
            patch.object(runner, "add_pypi_package") as mock_pypi,
        ):
            runner.add_package("numpy")
            mock_conda.assert_called_once_with("numpy", None)
            mock_pypi.assert_not_called()

    def test_conda_not_found_routes_to_pypi(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_exists_in_conda", return_value=False),
            patch.object(runner, "add_conda_package") as mock_conda,
            patch.object(runner, "add_pypi_package") as mock_pypi,
        ):
            runner.add_package("django-typer")
            mock_conda.assert_not_called()
            mock_pypi.assert_called_once_with("django-typer", None)

    def test_pypi_fails_raises_runtime_error(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_exists_in_conda", return_value=False),
            patch.object(
                runner,
                "add_pypi_package",
                side_effect=subprocess.CalledProcessError(1, "pixi"),
            ),
        ):
            with pytest.raises(RuntimeError, match="not found in conda or pypi"):
                runner.add_package("nope")

    def test_feature_passthrough(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_exists_in_conda", return_value=True),
            patch.object(runner, "add_conda_package") as mock_conda,
        ):
            runner.add_package("ruff", feature="dev")
            mock_conda.assert_called_once_with("ruff", "dev")

    def test_add_conda_package_direct(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.add_conda_package("numpy")
            mock_run.assert_called_once_with("add", "numpy")

    def test_add_conda_package_with_feature(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.add_conda_package("numpy", feature="dev")
            mock_run.assert_called_once_with("add", "numpy", "--feature", "dev")

    def test_add_pypi_package_direct(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.add_pypi_package("django-typer")
            mock_run.assert_called_once_with("add", "--pypi", "django-typer")

    def test_add_pypi_package_with_feature(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            runner.add_pypi_package("django-typer", feature="dev")
            mock_run.assert_called_once_with(
                "add", "--pypi", "django-typer", "--feature", "dev"
            )

    def test_extras_bypasses_conda_routes_to_pypi(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_exists_in_conda") as mock_exists,
            patch.object(runner, "add_conda_package") as mock_conda,
            patch.object(runner, "add_pypi_package") as mock_pypi,
        ):
            runner.add_package("django-storages[s3]<2")
            mock_exists.assert_not_called()
            mock_conda.assert_not_called()
            mock_pypi.assert_called_once_with("django-storages[s3]<2", None)

    def test_extras_with_feature_routes_to_pypi(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_exists_in_conda") as mock_exists,
            patch.object(runner, "add_conda_package") as mock_conda,
            patch.object(runner, "add_pypi_package") as mock_pypi,
        ):
            runner.add_package("django-storages[s3]<2", feature="dev")
            mock_exists.assert_not_called()
            mock_conda.assert_not_called()
            mock_pypi.assert_called_once_with("django-storages[s3]<2", "dev")

    def test_extras_pypi_failure_raises(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(
                runner,
                "add_pypi_package",
                side_effect=subprocess.CalledProcessError(1, "pixi"),
            ),
        ):
            with pytest.raises(subprocess.CalledProcessError):
                runner.add_package("django-allauth[mfa]<66")

    def test_no_extras_still_checks_conda(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_exists_in_conda", return_value=True),
            patch.object(runner, "add_conda_package") as mock_conda,
            patch.object(runner, "add_pypi_package") as mock_pypi,
        ):
            runner.add_package("numpy")
            mock_conda.assert_called_once_with("numpy", None)
            mock_pypi.assert_not_called()

    def test_multiple_extras_bypasses_conda(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_exists_in_conda") as mock_exists,
            patch.object(runner, "add_conda_package") as mock_conda,
            patch.object(runner, "add_pypi_package") as mock_pypi,
        ):
            runner.add_package("twisted[http2,tls]<27")
            mock_exists.assert_not_called()
            mock_conda.assert_not_called()
            mock_pypi.assert_called_once_with("twisted[http2,tls]<27", None)


# ---------------------------------------------------------------------------
# remove_package / remove_conda_package / remove_pypi_package
# ---------------------------------------------------------------------------


class TestRemovePackage:
    def test_conda_installed_routes_to_remove_conda(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_find_installed_source", return_value="conda"),
            patch.object(runner, "remove_conda_package") as mock_conda,
            patch.object(runner, "remove_pypi_package") as mock_pypi,
        ):
            runner.remove_package("numpy")
            mock_conda.assert_called_once_with("numpy", None)
            mock_pypi.assert_not_called()

    def test_pypi_installed_routes_to_remove_pypi(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_find_installed_source", return_value="pypi"),
            patch.object(runner, "remove_conda_package") as mock_conda,
            patch.object(runner, "remove_pypi_package") as mock_pypi,
        ):
            runner.remove_package("django-typer")
            mock_conda.assert_not_called()
            mock_pypi.assert_called_once_with("django-typer", None)

    def test_not_installed_returns_none(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "_find_installed_source", return_value=None):
            assert runner.remove_package("nope") is None

    def test_remove_package_idempotent(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with (
            patch.object(runner, "_find_installed_source", side_effect=["conda", None]),
            patch.object(runner, "remove_conda_package") as mock_remove,
        ):
            runner.remove_package("numpy")
            assert mock_remove.call_count == 1
            runner.remove_package("numpy")
            assert mock_remove.call_count == 1

    def test_remove_conda_package_idempotent(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(
            runner,
            "run_pixi_command",
            side_effect=subprocess.CalledProcessError(1, "pixi"),
        ):
            assert runner.remove_conda_package("nope") is None

    def test_remove_conda_package_succeeds(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            result = runner.remove_conda_package("numpy")
            assert result is mock_run.return_value
            mock_run.assert_called_once_with("remove", "numpy")

    def test_remove_pypi_package_idempotent(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(
            runner,
            "run_pixi_command",
            side_effect=subprocess.CalledProcessError(1, "pixi"),
        ):
            assert runner.remove_pypi_package("nope") is None

    def test_remove_pypi_package_succeeds(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            result = runner.remove_pypi_package("django-typer")
            assert result is mock_run.return_value
            mock_run.assert_called_once_with("remove", "--pypi", "django-typer")


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestInit:
    def test_explicit_backend_root(self):
        root = Path("/custom/backend")
        runner = PixiRunner(backend_root=root)
        assert runner.backend_root == root

    def test_falls_back_to_django_config(self):
        with patch("djdevx.utils.django.pixi_runner.DjangoConfig") as mock_config_class:
            mock_config = MagicMock()
            mock_config.django_backend_root = Path("/auto/backend")
            mock_config_class.return_value = mock_config

            runner = PixiRunner()
            assert runner.backend_root == Path("/auto/backend")


# ---------------------------------------------------------------------------
# run_manage_command
# ---------------------------------------------------------------------------


class TestRunManageCommand:
    def test_delegates_to_run_pixi_command(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
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
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch("subprocess.run") as mock_sub_run:
            runner.run_pixi_command("add", "numpy")
            mock_sub_run.assert_called_once()
            call_args = mock_sub_run.call_args[0][0]
            assert call_args == ["pixi", "add", "numpy"]
            assert mock_sub_run.call_args[1]["cwd"] == Path("/tmp")
            assert mock_sub_run.call_args[1]["check"] is True

    def test_check_false(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch("subprocess.run") as mock_sub_run:
            runner.run_pixi_command("search", "pkg", check=False)
            assert mock_sub_run.call_args[1]["check"] is False


# ---------------------------------------------------------------------------
# list_dependencies
# ---------------------------------------------------------------------------


class TestListDependencies:
    def test_parses_normal_output(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
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
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            assert runner.list_dependencies() == []

    def test_with_environment(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch.object(runner, "run_pixi_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            runner.list_dependencies(environment="dev")
            mock_run.assert_called_once()
            args = mock_run.call_args[0]
            assert "--environment" in args
            assert args[-1] == "dev"


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------


class TestRunCommand:
    def test_delegates_to_subprocess_run(self):
        runner = PixiRunner(backend_root=Path("/tmp"))
        with patch("subprocess.run") as mock_sub_run:
            runner.run_command(["echo", "hello"])
            mock_sub_run.assert_called_once_with(
                ["echo", "hello"], cwd=Path("/tmp"), check=True
            )
