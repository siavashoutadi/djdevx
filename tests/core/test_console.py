"""Tests for the NestedStep / step_group rendering helper."""

from io import StringIO

from rich.console import Console

from djdevx.core.console import print_console


def _capture():
    buf = StringIO()
    console = Console(file=buf, width=120, force_terminal=False)
    old = print_console._console
    print_console._console = console
    return buf, old


def test_step_group_renders_open_children_done():
    buf, old = _capture()
    try:
        group = print_console.step_group("starting otel", done="started otel")
        group.ok("installed otel")
        group.ok("started on port 57189")
        group.ok("set OTEL_COLLECTOR_PORT=57189")
        group.done()
    finally:
        print_console._console = old
    out = buf.getvalue()
    assert "starting otel" in out
    assert "installed otel" in out
    assert "started on port 57189" in out
    assert "set OTEL_COLLECTOR_PORT=57189" in out
    assert "started otel" in out
    lines = [line for line in out.splitlines() if line.strip()]
    assert lines[0].startswith("\u2610")  # ☐ open
    assert lines[-1].startswith("\u2611")  # ☑ done
    for line in lines[1:-1]:
        assert line.startswith("  \u2713")  # "  ✓ child"


def test_step_group_default_done_message():
    buf, old = _capture()
    try:
        group = print_console.step_group("Purging")
        group.ok("removing data")
        group.done()
    finally:
        print_console._console = old
    out = buf.getvalue()
    assert "Purging done" in out


def test_step_group_context_manager():
    buf, old = _capture()
    try:
        with print_console.step_group("Stopping Redis", done="stopped Redis") as step:
            step.ok("stopped redis on port 6379")
    finally:
        print_console._console = old
    out = buf.getvalue()
    assert "Stopping Redis" in out
    assert "stopped redis on port 6379" in out
    assert "stopped Redis" in out


def test_step_group_info_child():
    buf, old = _capture()
    try:
        with print_console.step_group("Checking", done="Checked") as step:
            step.info("a footnote")
    finally:
        print_console._console = old
    out = buf.getvalue()
    assert "\u2610" in out
    assert "  a footnote" in out
    assert "\u2611" in out


def test_section_header():
    buf, old = _capture()
    try:
        print_console.section("Services")
    finally:
        print_console._console = old
    assert "Services" in buf.getvalue()


def test_rule_rendered():
    buf, old = _capture()
    try:
        print_console.rule()
    finally:
        print_console._console = old
    # Rule adds a horizontal line; check non-empty output
    assert len(buf.getvalue()) > 0


def test_link_rendered():
    buf = StringIO()
    console = Console(file=buf, width=120, force_terminal=True)
    old = print_console._console
    print_console._console = console
    try:
        print_console.link("Click me", "https://example.com")
    finally:
        print_console._console = old
    assert "Click me" in buf.getvalue()
    assert "https://example.com" in buf.getvalue()
