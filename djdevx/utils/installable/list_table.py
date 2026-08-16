from ..console.print import GREEN_CHECK_MARK, RED_CROSS_MARK, print_console
from .tracking import get_available_names, get_display_name, get_installed_names


def build_list_table(cls, label: str) -> None:
    installed = get_installed_names(cls)
    all_names = get_available_names(cls)

    installed_names = sorted(n for n in all_names if n in installed)
    not_installed_names = sorted(n for n in all_names if n not in installed)

    table = print_console.build_table(
        f"{label}s",
        [
            ("", {"width": 1, "no_wrap": True}),
            (label, {}),
            ("Display Name", {}),
        ],
    )

    for name in installed_names:
        table.add_row(
            GREEN_CHECK_MARK,
            name,
            get_display_name(cls, name),
        )

    for name in not_installed_names:
        table.add_row(
            RED_CROSS_MARK,
            name,
            get_display_name(cls, name),
        )

    print_console.table(table)
