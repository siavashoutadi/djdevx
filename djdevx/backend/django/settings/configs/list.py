"""
configs list — table of config vars with source (dev/prod resolve chain).
"""

from pathlib import Path

import typer
from rich.table import Table

from .....utils.console.print import CHECK_MARK, CROSS_MARK, ELLIPSIS, print_console
from .....utils.djdevx_config.backend.django import DjangoConfig
from .....utils.django.setting_collector import SettingCollector

from .._source import (
    DEV,
    PROD,
    ConfigSource,
    resolve_config_source_dev,
    resolve_config_source_prod,
    resolve_config_value_dev,
    resolve_config_value_prod,
)

app = typer.Typer(no_args_is_help=True)


def _format_value(value) -> str:
    if value is None:
        return "[red](none)[/red]"
    raw = repr(value)
    return raw if len(raw) <= 50 else raw[:47] + ELLIPSIS


ENV_CONFIG = {
    DEV: {
        "resolve_source": resolve_config_source_dev,
        "resolve_value": resolve_config_value_dev,
    },
    PROD: {
        "resolve_source": resolve_config_source_prod,
        "resolve_value": resolve_config_value_prod,
    },
}


def _list(result, backend_root: Path, env: str) -> None:
    cfg = ENV_CONFIG[env]
    table = Table(
        title=f"Config vars ({env})",
        title_style="bold cyan",
        header_style="bold",
        border_style="bright_black",
        show_lines=False,
    )
    table.add_column("Status", width=8, justify="center", no_wrap=True)
    table.add_column("Name", style="bold", min_width=16, no_wrap=True)
    table.add_column("Type", style="dim", min_width=10, no_wrap=True)
    table.add_column("Source", style="dim", overflow="ellipsis")
    table.add_column(
        "Value", style="dim italic", min_width=24, no_wrap=True, overflow="ellipsis"
    )

    for config_var in result.config_vars:
        source = cfg["resolve_source"](config_var, backend_root)
        status = (
            f"[green]{CHECK_MARK}[/green]"
            if source != ConfigSource.MISSING
            else f"[red]{CROSS_MARK}[/red]"
        )
        value_str = _format_value(cfg["resolve_value"](config_var, backend_root))
        table.add_row(
            status, config_var.name, config_var.type_annotation, source, value_str
        )

    print_console.table(table)


@app.command("dev")
def list_dev() -> None:
    """
    List config vars resolved via the dev chain: os.environ > .env > dev default.
    """
    _run(DEV)


@app.command("prod")
def list_prod() -> None:
    """
    List config vars resolved via the prod chain: /run/configs/app-config > .env.prod > prod default.
    """
    _run(PROD)


def _run(env: str) -> None:
    pm = DjangoConfig()
    backend_root = pm.django_backend_root
    collector = SettingCollector(backend_root)
    result = collector.collect()

    if not result.config_vars:
        print_console.info("No config vars declared in this project.")
        return

    _list(result, backend_root, env)
