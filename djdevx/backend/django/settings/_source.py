"""
Shared source-resolution logic for configs and secrets.
"""

import atexit
import os
import readline
from enum import StrEnum
from pathlib import Path

from dotenv import dotenv_values

from ....utils.django.secret_manager import SecretManager

DEV = "dev"
PROD = "prod"


class ConfigSource(StrEnum):
    OS_ENVIRON = "os.environ"
    DOT_ENV = ".env"
    RUN_CONFIGS = "/run/configs/app-config"
    ENV_PROD = ".env.prod"
    DEV_DEFAULT = "dev default"
    PROD_DEFAULT = "prod default"
    MISSING = "(missing)"


class SecretSource(StrEnum):
    DEV_DEFAULT = "dev default"
    PROD_DEFAULT = "prod default"
    MISSING = "(missing)"


def read_env_file(env_path: Path) -> dict[str, str | None]:
    """Read a KEY=VALUE env file into a dict."""
    return dotenv_values(env_path)


def read_dot_env(project_path: Path) -> dict[str, str | None]:
    return read_env_file(project_path / ".env")


def read_env_prod(project_path: Path) -> dict[str, str | None]:
    return read_env_file(project_path / ".env.prod")


def resolve_config_source_dev(config_var, backend_root: Path) -> str:
    key = config_var.name.upper()
    if key in os.environ:
        return ConfigSource.OS_ENVIRON
    dot_env = read_dot_env(backend_root)
    if key in dot_env:
        return ConfigSource.DOT_ENV
    if config_var.dev_default is not None:
        return ConfigSource.DEV_DEFAULT
    return ConfigSource.MISSING


def resolve_config_source_prod(config_var, backend_root: Path) -> str:
    key = config_var.name.upper()
    if key in os.environ:
        return ConfigSource.OS_ENVIRON
    config_file = Path(ConfigSource.RUN_CONFIGS)
    if config_file.exists():
        config_vars = read_env_file(config_file)
        if key in config_vars:
            return ConfigSource.RUN_CONFIGS
    env_prod = read_env_prod(backend_root)
    if key in env_prod:
        return ConfigSource.ENV_PROD
    if config_var.prod_default is not None:
        return ConfigSource.PROD_DEFAULT
    return ConfigSource.MISSING


def resolve_config_value_dev(config_var, backend_root: Path):
    key = config_var.name.upper()
    if key in os.environ:
        return os.environ[key]
    dot_env = read_dot_env(backend_root)
    if key in dot_env:
        return dot_env[key]
    return config_var.dev_default


def resolve_config_value_prod(config_var, backend_root: Path):
    key = config_var.name.upper()
    if key in os.environ:
        return os.environ[key]
    config_file = Path(ConfigSource.RUN_CONFIGS)
    if config_file.exists():
        config_vars = read_env_file(config_file)
        if key in config_vars:
            return config_vars[key]
    env_prod = read_env_prod(backend_root)
    if key in env_prod:
        return env_prod[key]
    return config_var.prod_default


def resolve_secret_source_dev(secret, backend_root: Path) -> str:
    dev_manager = SecretManager(backend_root)
    run_dir = Path("/run/secrets")

    if dev_manager.has_secret(secret.name):
        return f".secrets/{secret.name}"
    if (run_dir / secret.name).exists():
        return f"/run/secrets/{secret.name}"
    if secret.has_dev_default:
        return SecretSource.DEV_DEFAULT
    return SecretSource.MISSING


def resolve_secret_source_prod(secret, backend_root: Path) -> str:
    prod_manager = SecretManager(backend_root, ".secrets.prod")
    run_dir = Path("/run/secrets")

    if (run_dir / secret.name).exists():
        return f"/run/secrets/{secret.name}"
    if prod_manager.has_secret(secret.name):
        return f".secrets.prod/{secret.name}"
    if secret.prod_default is not None:
        return SecretSource.PROD_DEFAULT
    return SecretSource.MISSING


def setup_readline() -> None:
    """Enable readline history for interactive prompts."""
    ddx_dir = Path.home() / ".djdevx"
    ddx_dir.mkdir(exist_ok=True)
    histfile = ddx_dir / "readline_history"
    try:
        readline.read_history_file(str(histfile))
    except FileNotFoundError:
        pass
    atexit.register(readline.write_history_file, str(histfile))
