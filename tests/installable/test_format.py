"""Tests for djdevx.installable.ops.format retry / reporting behavior."""

import subprocess
from pathlib import Path
from unittest import mock

from djdevx.installable.ops.format import (
    _is_stable,
    format_all_files_in_project,
    format_files,
)


class _Step:
    def __init__(self):
        self.ok_calls = []
        self.info_calls = []

    def ok(self, message):
        self.ok_calls.append(message)

    def info(self, message):
        self.info_calls.append(message)


def _result(returncode):
    return subprocess.CompletedProcess(args=[], returncode=returncode)


def _runner(results):
    runner = mock.MagicMock()
    runner.run_pixi_command.side_effect = results
    return runner


def test_first_run_ok_no_retry():
    runner = _runner([_result(99)])
    assert _is_stable(_result(0), runner, "run", "prek", "run") is True
    assert runner.run_pixi_command.call_count == 0


def test_fixer_first_run_then_stable():
    runner = _runner([_result(0)])
    assert _is_stable(_result(1), runner, "run", "prek", "run") is True
    assert runner.run_pixi_command.call_count == 1


def test_persistent_failure_reports():
    runner = _runner([_result(1)])
    assert _is_stable(_result(1), runner, "run", "prek", "run") is False
    assert runner.run_pixi_command.call_count == 1


def test_format_files_stable_after_fixer(tmp_path):
    step = _Step()
    runner = _runner([_result(1), _result(0)])
    with mock.patch("djdevx.installable.ops.format.PixiRunner", return_value=runner):
        format_files([Path("a.py")], project_root=tmp_path, step=step)
    assert step.ok_calls == ["Files formatted."]
    assert step.info_calls == []
    assert runner.run_pixi_command.call_count == 2


def test_format_files_persistent_failure_reports(tmp_path):
    step = _Step()
    runner = _runner([_result(1), _result(1)])
    with mock.patch("djdevx.installable.ops.format.PixiRunner", return_value=runner):
        format_files([Path("a.py")], project_root=tmp_path, step=step)
    assert step.ok_calls == []
    assert len(step.info_calls) == 1
    assert "prek run --files" in step.info_calls[0]


def test_format_all_stable_after_fixer(tmp_path):
    step = _Step()
    runner = _runner([_result(1), _result(0)])
    with mock.patch("djdevx.installable.ops.format.PixiRunner", return_value=runner):
        format_all_files_in_project(project_root=tmp_path, step=step)
    assert step.ok_calls == ["Files formatted."]
    assert step.info_calls == []


def test_format_all_persistent_failure_reports(tmp_path):
    step = _Step()
    runner = _runner([_result(1), _result(1)])
    with mock.patch("djdevx.installable.ops.format.PixiRunner", return_value=runner):
        format_all_files_in_project(project_root=tmp_path, step=step)
    assert step.ok_calls == []
    assert len(step.info_calls) == 1
    assert "prek run --all-files" in step.info_calls[0]


def test_format_all_failure_preserves_details_commands(tmp_path):
    step = _Step()
    runner = _runner([_result(0), _result(99)])
    with mock.patch("djdevx.installable.ops.format.PixiRunner", return_value=runner):
        format_all_files_in_project(project_root=tmp_path, step=step)
    assert step.ok_calls == ["Files formatted."]
