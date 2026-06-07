"""
configs verify — exit 1 if any config var missing for dev/prod.
"""

from pathlib import Path

import typer

from .....utils.console.print import CROSS_MARK, print_console
from .....utils.djdevx_config.backend.django import DjangoConfig
from .....utils.django.setting_collector import SettingCollector

from .._source import (
    DEV,
    PROD,
    ConfigSource,
    resolve_config_source_dev,
    resolve_config_source_prod,
)

app = typer.Typer(no_args_is_help=True)


ENV_CONFIG = {
    DEV: {
        "resolve_source": resolve_config_source_dev,
        "error_suffix": f"with no {DEV} default",
    },
    PROD: {
        "resolve_source": resolve_config_source_prod,
        "error_suffix": "",
        "fix_cmd": f"init {PROD}",
    },
}


def _verify(result, backend_root: Path, env: str) -> None:
    cfg = ENV_CONFIG[env]
    missing: list[str] = []
    for config_var in result.config_vars:
        if cfg["resolve_source"](config_var, backend_root) == ConfigSource.MISSING:
            missing.append(config_var.name)

    if missing:
        msg = f"{len(missing)} config var(s) missing{cfg['error_suffix']}:"
        print_console.error(msg)
        for name in missing:
            typer.echo(f"  {CROSS_MARK} {name}")
        fix_cmd = cfg.get("fix_cmd")
        if fix_cmd:
            typer.echo(f"\nRun: ddx backend django settings configs {fix_cmd}")
        raise typer.Exit(code=1)

    print_console.success(f"All {len(result.config_vars)} config var(s) are present.")


@app.command("dev")
def verify_dev() -> None:
    """
    Verify config vars are present for dev (env vars / .env).
    Exits with code 1 if any config var without a dev default is missing.
    """
    _run(DEV)


@app.command("prod")
def verify_prod() -> None:
    """
    Verify config vars are present for prod (.env.prod).
    Exits with code 1 if any config var is missing entirely.
    """
    _run(PROD)


def _run(env: str) -> None:
    pm = DjangoConfig()
    backend_root = pm.django_backend_root
    collector = SettingCollector(backend_root)
    result = collector.collect()

    _verify(result, backend_root, env)
