"""Secrets management sub-commands."""

from typing import Any, Literal

import typer

from ...utils.console.print import (
    GREEN_CHECK_MARK,
    RED_CROSS_MARK,
    YELLOW_CHECKMARK,
    print_console,
)
from ...utils.project.project_structure import ProjectStructure
from ...utils.project.secret_manager import SecretManager
from ...utils.project.setting_collector import SettingCollector
from ..source import (
    DEV,
    PROD,
    SecretSource,
    resolve_secret_source_dev,
    resolve_secret_source_prod,
)

app = typer.Typer(no_args_is_help=True)

ENV_CONFIG_LIST = {
    DEV: {"resolve_source": resolve_secret_source_dev},
    PROD: {"resolve_source": resolve_secret_source_prod},
}


# ------ secrets list ------


@app.command(name="list")
def list_secrets(
    env: Literal["dev", "prod"] = typer.Argument(help="Environment: dev or prod"),
) -> None:
    """List secrets for the given environment."""
    try:
        project_root = ProjectStructure().root
    except RuntimeError:
        print_console.info("Not in a djdevx project. Run `ddx new` first.")
        return

    collector = SettingCollector(project_root)
    result = collector.collect()

    if not result.secrets:
        print_console.info("No secrets declared in this project.")
        return

    cfg = ENV_CONFIG_LIST[env]
    with print_console.table(
        f"Secrets ({env})",
        [
            ("Status", {"width": 8, "justify": "center", "no_wrap": True}),
            ("Name", {"style": "bold", "min_width": 16, "no_wrap": True}),
            ("Source", {"style": "dim", "overflow": "ellipsis"}),
        ],
        show_lines=False,
    ) as tbl:
        for secret in result.secrets:
            source = cfg["resolve_source"](secret, project_root)
            if source == SecretSource.CLASS_DEFAULT:
                status = YELLOW_CHECKMARK
            elif source != SecretSource.MISSING:
                status = GREEN_CHECK_MARK
            else:
                status = RED_CROSS_MARK
            tbl.add_row(status, secret.name, source)


# ------ secrets init ------


@app.command()
def init(
    env: Literal["dev", "prod"] = typer.Argument(help="Environment: dev or prod"),
) -> None:
    """Initialize secrets for the given environment."""
    try:
        project_root = ProjectStructure().root
    except RuntimeError:
        print_console.info("Not in a djdevx project. Run `ddx new` first.")
        return

    collector = SettingCollector(project_root)
    result = collector.collect()

    if not result.secrets:
        print_console.info("No secrets declared in this project.")
        return

    if env == DEV:
        _init_dev(result, project_root)
    elif env == PROD:
        _init_prod(result, project_root)


def _init_dev(result, project_root) -> None:
    secret_manager = SecretManager(project_root)
    generated = 0
    prompted = 0
    skipped = 0
    dev_default_skipped = 0

    for secret in result.secrets:
        source = resolve_secret_source_dev(secret, project_root)
        if source != SecretSource.MISSING and source != SecretSource.DEV_DEFAULT:
            skipped += 1
            continue

        if source == SecretSource.DEV_DEFAULT:
            dev_default_skipped += 1
            continue

        if secret.generator is not None:
            value = secret.generator()
            secret_manager.write_secret(secret.name, value)
            print_console.ok(f"Generated  {secret.name}")
            generated += 1
        else:
            print_console.info(f"\nSecret required: {secret.name}")
            print_console.info(f"Source: {secret.source_file.name}")
            value = typer.prompt(
                f"Enter value for {secret.name}",
                hide_input=True,
                confirmation_prompt=True,
            )
            secret_manager.write_secret(secret.name, value)
            print_console.ok(f"Saved     {secret.name}")
            prompted += 1

    parts = []
    if generated:
        parts.append(f"{generated} generated")
    if prompted:
        parts.append(f"{prompted} from prompt")
    if skipped:
        parts.append(f"{skipped} already present (skipped)")
    if dev_default_skipped:
        parts.append(f"{dev_default_skipped} using dev default (skipped)")

    summary = ", ".join(parts) if parts else "nothing to do"
    print_console.ok(f"Secrets ready: {summary}.")


def _init_prod(result, project_root) -> None:
    prod_manager = SecretManager(project_root, ".secrets.prod")
    generated = 0
    prompted = 0
    skipped = 0

    for secret in result.secrets:
        if resolve_secret_source_prod(secret, project_root) != SecretSource.MISSING:
            skipped += 1
            continue

        if secret.generator is not None:
            value = secret.generator()
            prod_manager.write_secret(secret.name, value)
            print_console.ok(f"Generated  {secret.name}")
            generated += 1
        else:
            print_console.info(f"\nSecret required: {secret.name}")
            print_console.info(f"Source: {secret.source_file.name}")
            value = typer.prompt(
                f"Enter value for {secret.name}",
                hide_input=True,
                confirmation_prompt=True,
            )
            prod_manager.write_secret(secret.name, value)
            print_console.ok(f"Saved     {secret.name}")
            prompted += 1

    parts = []
    if generated:
        parts.append(f"{generated} generated")
    if prompted:
        parts.append(f"{prompted} from prompt")
    if skipped:
        parts.append(f"{skipped} already present (skipped)")

    summary = ", ".join(parts) if parts else "nothing to do"
    print_console.ok(f"Prod secrets ready: {summary}.")


# ------ secrets verify ------


ENV_CONFIG_VERIFY: dict[str, dict[str, Any]] = {
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


@app.command()
def verify(
    env: Literal["dev", "prod"] = typer.Argument(help="Environment: dev or prod"),
) -> None:
    """Verify secrets completeness."""
    try:
        project_root = ProjectStructure().root
    except RuntimeError:
        print_console.info("Not in a djdevx project. Run `ddx new` first.")
        raise typer.Exit(code=1)

    collector = SettingCollector(project_root)
    result = collector.collect()

    cfg = ENV_CONFIG_VERIFY[env]
    missing: list[str] = []
    optional: list[str] = []
    for secret in result.secrets:
        source = cfg["resolve_source"](secret, project_root)
        if source == SecretSource.MISSING:
            missing.append(secret.name)
        elif source == SecretSource.CLASS_DEFAULT:
            optional.append(secret.name)

    if optional:
        names = ", ".join(optional)
        print_console.info(f"{len(optional)} optional secret(s) using class defaults:")
        typer.echo(f"  {names}")

    if missing:
        print_console.error(f"{len(missing)} secret(s) missing {cfg['error_msg']}:")
        for name in missing:
            typer.echo(f"{RED_CROSS_MARK} {name}")
        typer.echo(f"\nRun: ddx settings secrets {cfg['fix_cmd']}")
        raise typer.Exit(code=1)

    print_console.ok(f"All {len(result.secrets)} secret(s) are present.")
