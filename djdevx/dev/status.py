"""ddx dev status — report on the local dev environment."""

from ..settings.configs import list_configs
from ..settings.secrets import list_secrets
from ..utils.console.print import GREEN_CHECK_MARK, RED_CROSS_MARK, print_console
from ..utils.django.manage_commands import ManageCommands
from ..utils.project.pixi_runner import PixiRunner
from ..services import resolve_dev_services
from ..settings.source import DEV


def status() -> None:
    """Show service up/down, migrate state, and settings state."""
    services = resolve_dev_services()
    runner = PixiRunner()
    commands = ManageCommands(runner)

    states: list[tuple] = []
    with print_console.table(
        "Dev services",
        [
            ("Status", {"width": 8, "justify": "center", "no_wrap": True}),
            ("Service", {"style": "bold", "min_width": 12, "no_wrap": True}),
            ("Type", {"style": "dim", "min_width": 10, "no_wrap": True}),
        ],
    ) as tbl:
        for service in services:
            is_up = service.is_up()
            states.append((service, is_up))
            status_mark = GREEN_CHECK_MARK if is_up else RED_CROSS_MARK
            tbl.add_row(status_mark, service.display_name, service.name)

    _report_issues(states)

    migrate_ok = not commands.migrations_pending()
    print_console.info(f"Migrations: {'up to date' if migrate_ok else 'pending'}")

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
