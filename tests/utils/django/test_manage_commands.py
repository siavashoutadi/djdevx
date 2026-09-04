"""Tests for djdevx.utils.django.manage_commands.ManageCommands."""

import subprocess
from unittest.mock import MagicMock, patch

from djdevx.utils.django.manage_commands import ManageCommands
from djdevx.core.process import PixiRunner


class TestRun:
    def test_delegates_to_pixi_runner(self):
        runner = MagicMock()
        commands = ManageCommands(runner)
        commands.run("startapp", "myapp", check=False)
        runner.run_manage_command.assert_called_once_with(
            "startapp", "myapp", check=False
        )

    def test_returns_completed_process(self):
        runner = MagicMock()
        result = subprocess.CompletedProcess([], returncode=0)
        runner.run_manage_command.return_value = result
        commands = ManageCommands(runner)
        assert commands.run("migrate") is result


class TestMigrationsPending:
    def test_true_when_returncode_nonzero(self):
        runner = MagicMock()
        runner.run_manage_command.return_value = subprocess.CompletedProcess(
            [], returncode=1
        )
        commands = ManageCommands(runner)
        assert commands.migrations_pending() is True
        runner.run_manage_command.assert_called_once_with(
            "migrate", "--check", check=False
        )

    def test_false_when_up_to_date(self):
        runner = MagicMock()
        runner.run_manage_command.return_value = subprocess.CompletedProcess(
            [], returncode=0
        )
        commands = ManageCommands(runner)
        assert commands.migrations_pending() is False


class TestDefaultRunner:
    def test_builds_own_pixi_runner(self):
        with patch("djdevx.utils.django.manage_commands.PixiRunner") as pixi_cls:
            commands = ManageCommands()
            assert commands._runner is pixi_cls.return_value
            pixi_cls.assert_called_once_with()


class TestWithRealRunner:
    def test_accepts_pixi_runner(self, tmp_path):
        commands = ManageCommands(PixiRunner(project_root=tmp_path))
        assert commands._runner.project_root == tmp_path
