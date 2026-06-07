"""
secrets verify — exit 1 if any secret missing for dev/prod.
"""

from pathlib import Path

import typer

from .....utils.console.print import CROSS_MARK, print_console
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
        "error_msg": "with no fallback",
        "fix_cmd": f"init {DEV}",
    },
    PROD: {
        "resolve_source": resolve_secret_source_prod,
        "error_msg": "from .secrets.prod/",
        "fix_cmd": f"init {PROD}",
    },
}


def _verify(result, backend_root: Path, env: str) -> None:
    cfg = ENV_CONFIG[env]
    missing: list[str] = []
    for secret in result.secrets:
        if cfg["resolve_source"](secret, backend_root) == SecretSource.MISSING:
            missing.append(secret.name)

    if missing:
        print_console.error(f"{len(missing)} secret(s) missing {cfg['error_msg']}:")
        for name in missing:
            typer.echo(f"  {CROSS_MARK} {name}")
        typer.echo(f"\nRun: ddx backend django settings secrets {cfg['fix_cmd']}")
        raise typer.Exit(code=1)

    print_console.success(f"All {len(result.secrets)} secret(s) are present.")


def _run(env: str) -> None:
    pm = DjangoConfig()
    backend_root = pm.django_backend_root
    collector = SettingCollector(backend_root)
    result = collector.collect()

    _verify(result, backend_root, env)


@app.command("dev")
def verify_dev() -> None:
    """
    Verify secrets are present for dev (.secrets/ + /run/secrets/).
    Exits with code 1 if any secret without a dev default is missing.
    """
    _run(DEV)


@app.command("prod")
def verify_prod() -> None:
    """
    Verify secrets are present for prod (.secrets.prod/).
    Exits with code 1 if any secret is missing with no prod default fallback.
    """
    _run(PROD)
