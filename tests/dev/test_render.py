"""Tests for the shared dev service/credentials table rendering."""

from unittest.mock import MagicMock, patch

from djdevx.dev.render import render_credentials_table, render_services_table
from djdevx.utils.console.print import print_console
from djdevx.utils.devcontainer.detect import DevelopmentContext, ServiceEndpoint


def _endpoint(name="postgres", display="PostgreSQL", port=5432, creds=None, url=None):
    return ServiceEndpoint(
        name=name,
        display_name=display,
        host="localhost",
        port=port,
        credentials=creds,
        url=url,
    )


def _native_ctx(*services):
    return DevelopmentContext(in_devcontainer=False, services=list(services))


def test_services_table_empty_prints_info():
    with patch.object(print_console, "info") as info:
        render_services_table(_native_ctx())
    info.assert_called_once_with("No dev services configured.")


def test_services_table_rows_and_title():
    ctx = _native_ctx(
        _endpoint(creds="s3cr3t", url="http://localhost:5432"),
        _endpoint("redis", "Redis", 6379),
    )
    table = MagicMock()
    with (
        patch.object(print_console, "table") as tbl_factory,
        patch.object(print_console, "info") as info,
    ):
        tbl_factory.return_value.__enter__.return_value = table
        render_services_table(ctx)
    info.assert_not_called()
    assert tbl_factory.call_args.args[0] == "Dev services (pixi-native)"
    rows = [call.args for call in table.add_row.call_args_list]
    assert rows == [
        ("PostgreSQL", "localhost", "5432", "http://localhost:5432"),
        ("Redis", "localhost", "6379", ""),
    ]


def test_services_table_devcontainer_title():
    ctx = DevelopmentContext(in_devcontainer=True, services=[_endpoint()])
    with (
        patch.object(print_console, "table") as tbl_factory,
        patch.object(print_console, "info"),
    ):
        tbl_factory.return_value.__enter__.return_value = MagicMock()
        render_services_table(ctx)
    assert (
        tbl_factory.call_args.args[0] == "Dev services (devcontainer / docker compose)"
    )


def test_credentials_table_lists_connect_blocks():
    ctx = _native_ctx(
        _endpoint(creds="s3cr3t", url="http://localhost:5432"),
        _endpoint("redis", "Redis", 0),
    )
    with (
        patch.object(print_console, "info") as info,
        patch.object(print_console, "section") as section,
        patch.object(print_console, "link"),
        patch.object(print_console, "rule"),
    ):
        render_credentials_table(ctx)
    lines = [call.args[0] for call in info.call_args_list]
    assert "  Credentials: s3cr3t" in lines
    assert "  Port: 5432" in lines
    assert "  Host: localhost" in lines
    # Zero port is omitted, missing credentials omitted for redis.
    assert not any("Port: 0" in line for line in lines)
    assert [call.args[0] for call in section.call_args_list] == [
        "PostgreSQL",
        "Redis",
    ]


def test_credentials_table_empty_prints_info():
    with patch.object(print_console, "info") as info:
        render_credentials_table(_native_ctx())
    info.assert_called_once_with("No dev services configured.")
