"""Tests for requirement commands."""

from typer.testing import CliRunner

from djdevx.main import app
from djdevx.requirement import REQUIRED_TOOLS
from djdevx.utils.system.tools import system_tools

runner = CliRunner()


def test_install_all_installed_exits_cleanly(monkeypatch):
    """Installing when every tool is present is a no-op."""
    monkeypatch.setattr(system_tools, "is_tool_installed", lambda _: True)
    result = runner.invoke(app, ["requirement", "install"])
    assert result.exit_code == 0
    assert "already installed" in result.output


def test_install_skips_already_installed_tool(monkeypatch):
    """A tool that is already installed is skipped."""
    monkeypatch.setattr(system_tools, "is_tool_installed", lambda _: True)
    result = runner.invoke(app, ["requirement", "install", "--tool", "git"])
    assert result.exit_code == 0
    assert "git is already installed" in result.output


def test_install_unknown_tool_fails(monkeypatch):
    """Unknown tools are rejected."""
    monkeypatch.setattr(system_tools, "is_tool_installed", lambda _: False)
    result = runner.invoke(app, ["requirement", "install", "--tool", "nope"])
    assert result.exit_code == 1
    assert "Unknown tool 'nope'" in result.output


def test_install_dry_run_prints_commands(monkeypatch):
    """Dry run prints install commands without executing them."""
    monkeypatch.setattr(system_tools, "is_tool_installed", lambda _: False)
    result = runner.invoke(
        app, ["requirement", "install", "--tool", "pixi", "--dry-run"]
    )
    assert result.exit_code == 0
    assert "$ curl -fsSL https://pixi.sh/install.sh | bash" in result.output


def test_install_unsupported_platform_fails(monkeypatch):
    """Non-Linux/macOS platforms are rejected."""
    monkeypatch.setattr(system_tools, "is_tool_installed", lambda _: False)
    monkeypatch.setattr("djdevx.requirement.sys.platform", "win32")
    result = runner.invoke(app, ["requirement", "install"])
    assert result.exit_code == 1
    assert "Linux and macOS only" in result.output


def test_required_tools():
    """The install command targets the same tools as verify."""
    assert REQUIRED_TOOLS == ("pixi", "git", "docker")
