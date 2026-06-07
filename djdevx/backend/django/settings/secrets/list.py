"""
secrets list — table of secrets with source (dev/prod resolve chain).
"""

from pathlib import Path

import typer
from rich.table import Table

from .....utils.console.print import CHECK_MARK, CROSS_MARK, print_console
from .....utils.djdevx_config.backend.django import DjangoConfig
from .....utils.django.setting_collector import SettingCollector

from .._source import (
    DEV,
    PROD,
    SecretSource,
    resolve_secret_source_dev,
    resolve_secret_source_prod,
)

app = typer.Typer(no_args_is_help=True)


ENV_CONFIG = {
    DEV: {
        "resolve_source": resolve_secret_source_dev,
    },
    PROD: {
        "resolve_source": resolve_secret_source_prod,
    },
}


def _list(result, backend_root: Path, env: str) -> None:
    cfg = ENV_CONFIG[env]
    table = Table(
        title=f"Secrets ({env})",
        title_style="bold cyan",
        header_style="bold",
        border_style="bright_black",
        show_lines=False,
    )
    table.add_column("Status", width=8, justify="center", no_wrap=True)
    table.add_column("Name", style="bold", min_width=16, no_wrap=True)
    table.add_column("Source", style="dim", overflow="ellipsis")

    for secret in result.secrets:
        source = cfg["resolve_source"](secret, backend_root)
        status = (
            f"[green]{CHECK_MARK}[/green]"
            if source != SecretSource.MISSING
            else f"[red]{CROSS_MARK}[/red]"
        )
        table.add_row(status, secret.name, source)

    print_console.table(table)


def _run(env: str) -> None:
    pm = DjangoConfig()
    backend_root = pm.django_backend_root
    collector = SettingCollector(backend_root)
    result = collector.collect()

    if not result.secrets:
        print_console.info("No secrets declared in this project.")
        return

    _list(result, backend_root, env)


@app.command("dev")
def list_dev() -> None:
    """
    List secrets resolved via the dev chain: .secrets/ > /run/secrets/ > dev default.
    """
    _run(DEV)


@app.command("prod")
def list_prod() -> None:
    """
    List secrets resolved via the prod chain: /run/secrets/ > .secrets.prod/ > prod default.
    """
    _run(PROD)
