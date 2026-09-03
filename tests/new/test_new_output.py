"""Tests for the NestedStep output of the ``ddx new`` scaffolding helpers."""

from io import StringIO
from pathlib import Path
from unittest import mock

from rich.console import Console

import djdevx.new.__init__ as new_mod
from djdevx.utils.console.print import print_console


def _capture():
    buf = StringIO()
    console = Console(file=buf, width=120, force_terminal=False)
    old = print_console._console
    print_console._console = console
    return buf, old


def _restore(old):
    print_console._console = old


class _Result:
    def __init__(self, returncode=0, stderr=""):
        self.returncode = returncode
        self.stderr = stderr


class _SuccessfulRun:
    def __call__(self, *args, **kwargs):
        return _Result(returncode=0, stderr="")


class FakePixi:
    def __init__(self, project_root):
        self.project_root = project_root
        self.calls = []

    def add_package(self, pkg, feature=None):
        self.calls.append((pkg, feature))

    @staticmethod
    def _extract_package_name(pkg):
        for sep in ("~", "<", ">", "=", "!", "@"):
            pkg = pkg.split(sep)[0]
        return pkg


def test_install_dependencies_ok_children_are_indented(tmp_path):
    buf, old = _capture()
    try:
        with mock.patch.object(new_mod, "PixiRunner", FakePixi):
            new_mod.install_dependencies(Path(tmp_path))
    finally:
        _restore(old)
    out = buf.getvalue()
    lines = [line for line in out.splitlines() if line.strip()]
    assert lines[0].startswith("\u2610 Installing dependencies")  # ☐ open
    assert lines[-1].startswith("\u2611 Dependencies are installed")  # ☑ done
    for line in lines[1:-1]:
        assert line.startswith("  \u2713"), line  # "  ✓ <pkg> is installed"
        assert "is installed" in line


def test_init_git_ok_children_are_indented(tmp_path):
    buf, old = _capture()
    try:
        with mock.patch.object(new_mod.subprocess, "run", _SuccessfulRun()):
            new_mod._init_git(Path(tmp_path), verbose=False)
    finally:
        _restore(old)
    out = buf.getvalue()
    lines = [line for line in out.splitlines() if line.strip()]
    assert lines[0].startswith("\u2610 Initializing the git repository")  # ☐
    assert lines[-1].startswith("\u2611 Git repository is initialized")  # ☑
    for line in lines[1:-1]:
        assert line.startswith("  \u2713"), line  # "  ✓ git init / add / commit"
