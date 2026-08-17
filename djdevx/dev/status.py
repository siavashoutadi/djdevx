"""ddx dev status — report on the local dev environment."""

from ..settings.configs import list_configs
from ..settings.secrets import list_secrets
from ..utils.console.print import GREEN_CHECK_MARK, RED_CROSS_MARK, print_console
from ..utils.django.manage_commands import ManageCommands
from ..utils.project.pixi_runner import PixiRunner
from ..utils.services import resolve_dev_services


def status() -> None:
    """Show service up/down, migrate state, and settings state."""
    services = resolve_dev_services()
    runner = PixiRunner()
    commands = ManageCommands(runner)

    table = print_console.build_table(
        "Dev services",
        [
            ("Status", {"width": 8, "justify": "center", "no_wrap": True}),
            ("Service", {"style": "bold", "min_width": 12, "no_wrap": True}),
            ("Type", {"style": "dim", "min_width": 10, "no_wrap": True}),
        ],
    )

    for service in services:
        status_mark = GREEN_CHECK_MARK if service.is_up() else RED_CROSS_MARK
        table.add_row(status_mark, service.display_name, service.name)

    print_console.table(table)

    migrate_ok = not commands.migrations_pending()
    print_console.info(f"Migrations: {'up to date' if migrate_ok else 'pending'}")

    list_secrets("dev")
    list_configs("dev")
