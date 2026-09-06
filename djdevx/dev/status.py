"""ddx dev status — report on the local dev environment."""

from ..settings.configs import list_configs
from ..settings.secrets import list_secrets
from djdevx.core.console import GREEN_CHECK_MARK, RED_CROSS_MARK, print_console
from ..utils.django.manage_commands import ManageCommands
from djdevx.core.process import PixiRunner
from ..services import resolve_dev_services
from ..settings.source import DEV


def status() -> None:
    """Show service up/down, migrate state, and settings state."""
    services = resolve_dev_services()
    runner = PixiRunner()
    commands = ManageCommands(runner)

    states: list[tuple] = [(service, service.is_up()) for service in services]

    for service in services:
        service._set_port_env(quiet=True)

    postgres_installed = any(service.name == "postgres" for service, _ in states)
    postgres_up = any(service.name == "postgres" and is_up for service, is_up in states)
    with print_console.step_group(
        "Checking for pending migrations...", done="Migration check complete"
    ) as group:
        if not postgres_installed:
            group.info("No PostgreSQL configured — skipped")
        elif not postgres_up:
            group.warning("PostgreSQL is down — skipped")
        else:
            pending = commands.migrations_pending()
            if pending is None:
                group.warning("Migrations: could not check (timed out)")
            elif pending:
                group.warning("Migrations: pending")
            else:
                group.ok("Migrations: up to date")

    with print_console.table(
        "Dev services",
        [
            ("Status", {"width": 8, "justify": "center", "no_wrap": True}),
            ("Service", {"style": "bold", "min_width": 12, "no_wrap": True}),
        ],
    ) as tbl:
        for service, is_up in states:
            status_mark = GREEN_CHECK_MARK if is_up else RED_CROSS_MARK
            tbl.add_row(status_mark, service.display_name)

    _report_issues(states)

    list_secrets(DEV)
    list_configs(DEV)


def _report_issues(states: list[tuple]) -> None:
    """Print a short diagnostic line for every service that is not up."""
    down = [(service, is_up) for service, is_up in states if not is_up]
    if not down:
        return
    print_console.warning(f"{len(down)} of {len(states)} service(s) are down:")
    for service, _ in down:
        print_console.fail(f"{service.display_name}: {service.describe_down()}")
