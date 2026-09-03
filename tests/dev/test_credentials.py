"""Tests for ddx dev credentials."""

from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.main import app
from djdevx.utils.devcontainer.detect import DevelopmentContext, ServiceEndpoint

runner = CliRunner()


def test_credentials_no_services(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    with patch(
        "djdevx.dev.credentials.collect_context",
        return_value=DevelopmentContext(in_devcontainer=False, services=[]),
    ):
        result = runner.invoke(app, ["dev", "credentials"])
    assert result.exit_code == 0
    assert "No dev services configured." in result.output


def test_credentials_prints_connect_ui(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "djdevx.toml").write_text("")
    ctx = DevelopmentContext(
        in_devcontainer=False,
        services=[
            ServiceEndpoint(
                name="postgres",
                display_name="PostgreSQL",
                host="localhost",
                port=5432,
                credentials="postgres",
                url=None,
            ),
            ServiceEndpoint(
                name="openobserve",
                display_name="OpenObserve",
                host="localhost",
                port=5080,
                url="http://localhost:5080",
            ),
        ],
    )
    with patch("djdevx.dev.credentials.collect_context", return_value=ctx):
        result = runner.invoke(app, ["dev", "credentials"])
    assert result.exit_code == 0
    assert "PostgreSQL" in result.output
    assert "Host: localhost" in result.output
    assert "Port: 5432" in result.output
    assert "Credentials: postgres" in result.output
    assert "OpenObserve" in result.output
    assert "Port: 5080" in result.output
    assert "http://localhost:5080" in result.output
    assert "[link=" not in result.output
