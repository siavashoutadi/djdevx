"""
secrets init — populates local dev secrets and prod secrets.
"""

import typer

from .....utils.console.print import print_console
from .....utils.djdevx_config.backend.django import DjangoConfig
from .....utils.django.setting_collector import SettingCollector
from .....utils.django.secret_manager import SecretManager
from .._source import (
    SecretSource,
    resolve_secret_source_dev,
    resolve_secret_source_prod,
)

app = typer.Typer(no_args_is_help=True)


@app.command("dev")
def init_dev() -> None:
    """
    Initialise local development secrets.

    Scans all settings files for SecretStr fields and ensures each has a
    value in .secrets/. Fields with registered generators are auto-populated;
    others prompt the user for input. Idempotent — skips already-present secrets.
    """
    config = DjangoConfig()
    backend_root = config.django_backend_root
    secret_manager = SecretManager(backend_root)
    collector = SettingCollector(backend_root)
    result = collector.collect()

    if not result.secrets:
        print_console.info("No secrets declared in this project.")
        return

    generated = 0
    prompted = 0
    skipped = 0
    dev_default_skipped = 0

    for secret in result.secrets:
        source = resolve_secret_source_dev(secret, backend_root)
        if source != SecretSource.MISSING and source != SecretSource.DEV_DEFAULT:
            skipped += 1
            continue

        if source == SecretSource.DEV_DEFAULT:
            dev_default_skipped += 1
            continue

        if secret.generator is not None:
            value = secret.generator()
            secret_manager.write_secret(secret.name, value)
            print_console.success(f"  Generated  {secret.name}")
            generated += 1
        else:
            print_console.info(f"\n  Secret required: {secret.name}")
            print_console.info(f"  Source: {secret.source_file.name}")
            value = typer.prompt(
                f"  Enter value for {secret.name}",
                hide_input=True,
                confirmation_prompt=True,
            )
            secret_manager.write_secret(secret.name, value)
            print_console.success(f"  Saved     {secret.name}")
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
    print_console.success(f"\nSecrets ready: {summary}.")


@app.command("prod")
def init_prod() -> None:
    """
    Initialise production secrets in .secrets.prod/.

    For each SecretStr field, auto-generates or prompts for the value and
    writes it to .secrets.prod/<name>. Idempotent — skips already-present
    entries.
    """
    config = DjangoConfig()
    backend_root = config.django_backend_root
    prod_manager = SecretManager(backend_root, ".secrets.prod")
    collector = SettingCollector(backend_root)
    result = collector.collect()

    if not result.secrets:
        print_console.info("No secrets declared in this project.")
        return

    generated = 0
    prompted = 0
    skipped = 0

    for secret in result.secrets:
        if resolve_secret_source_prod(secret, backend_root) != SecretSource.MISSING:
            skipped += 1
            continue

        if secret.generator is not None:
            value = secret.generator()
            prod_manager.write_secret(secret.name, value)
            print_console.success(f"  Generated  {secret.name}")
            generated += 1
        else:
            print_console.info(f"\n  Secret required: {secret.name}")
            print_console.info(f"  Source: {secret.source_file.name}")
            value = typer.prompt(
                f"  Enter value for {secret.name}",
                hide_input=True,
                confirmation_prompt=True,
            )
            prod_manager.write_secret(secret.name, value)
            print_console.success(f"  Saved     {secret.name}")
            prompted += 1

    parts = []
    if generated:
        parts.append(f"{generated} generated")
    if prompted:
        parts.append(f"{prompted} from prompt")
    if skipped:
        parts.append(f"{skipped} already present (skipped)")

    summary = ", ".join(parts) if parts else "nothing to do"
    print_console.success(f"\nProd secrets ready: {summary}.")
