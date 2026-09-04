"""Configs management sub-commands."""

import ast
import re
from typing import Any, Literal

import pydantic
import typer
from dotenv import set_key

from djdevx.core.console import (
    ELLIPSIS,
    GREEN_CHECK_MARK,
    Markup,
    RED_CROSS_MARK,
    YELLOW_CHECKMARK,
    print_console,
)
from djdevx.core.paths import ProjectStructure
from ...utils.project.setting_collector import SettingCollector
from ..source import (
    DEV,
    PROD,
    ConfigSource,
    resolve_config_source_dev,
    resolve_config_source_prod,
    resolve_config_value_dev,
    resolve_config_value_prod,
    setup_readline,
)

app = typer.Typer(no_args_is_help=True)

# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------


def _format_value(value) -> str:
    if value is None:
        return Markup("[red](none)[/red]")
    raw = repr(value)
    return raw if len(raw) <= 50 else raw[:47] + ELLIPSIS


_ENV_CONFIG_LIST = {
    DEV: {
        "resolve_source": resolve_config_source_dev,
        "resolve_value": resolve_config_value_dev,
    },
    PROD: {
        "resolve_source": resolve_config_source_prod,
        "resolve_value": resolve_config_value_prod,
    },
}


# ------ configs list ------


@app.command(name="list")
def list_configs(
    env: Literal["dev", "prod"] = typer.Argument(help="Environment: dev or prod"),
) -> None:
    """List config vars for the given environment."""
    try:
        project_root = ProjectStructure().root
    except RuntimeError:
        print_console.info("Not in a djdevx project. Run `ddx new` first.")
        return

    collector = SettingCollector(project_root)
    result = collector.collect()

    if not result.config_vars:
        print_console.info("No config vars declared in this project.")
        return

    cfg = _ENV_CONFIG_LIST[env]
    _print_configs_table(env, result, project_root, cfg)


def _print_configs_table(env: str, result, project_root, cfg: dict) -> None:
    """Render the full config vars status table."""
    with print_console.table(
        f"Config vars ({env})",
        [
            ("Status", {"width": 8, "justify": "center", "no_wrap": True}),
            ("Name", {"style": "bold", "min_width": 16, "no_wrap": True}),
            ("Type", {"style": "dim", "min_width": 10, "no_wrap": True}),
            ("Source", {"style": "dim", "overflow": "ellipsis"}),
            (
                "Value",
                {
                    "style": "dim italic",
                    "min_width": 24,
                    "no_wrap": True,
                    "overflow": "ellipsis",
                },
            ),
        ],
        show_lines=False,
    ) as tbl:
        for config_var in result.config_vars:
            source = cfg["resolve_source"](config_var, project_root)
            if source == ConfigSource.CLASS_DEFAULT:
                status = YELLOW_CHECKMARK
                value_str = "(class default)"
            elif source != ConfigSource.MISSING:
                status = GREEN_CHECK_MARK
                value_str = _format_value(
                    cfg["resolve_value"](config_var, project_root)
                )
            else:
                status = RED_CROSS_MARK
                value_str = _format_value(
                    cfg["resolve_value"](config_var, project_root)
                )
            tbl.add_row(
                status,
                config_var.name,
                config_var.type_annotation,
                source,
                value_str,
            )


# ------ configs init ------


_TYPE_HINTS: dict[str, str] = {
    "bool": "true/false, yes/no, or 1/0",
    "int": "an integer",
    "float": "a number",
    "EmailStr": "a valid email address, e.g. user@example.com",
}


def _expected_format_base(annotation: str) -> str:
    if annotation in _TYPE_HINTS:
        return _TYPE_HINTS[annotation]
    if annotation.startswith("Literal["):
        return f"one of: {annotation[8:-1]}"
    if annotation.startswith("Optional["):
        inner = annotation[9:-1]
        return f"{_expected_format_base(inner)} (or leave empty to skip)"
    if (
        annotation.startswith("list[")
        or annotation.startswith("dict[")
        or annotation.startswith("set[")
    ):
        return 'a JSON value, e.g. ["item1", "item2"] or {"key": "value"}'
    return "a valid value"


def _expected_format(annotation: str) -> str:
    return f"Expected {_expected_format_base(annotation)}"


def _pydantic_error_message(e: pydantic.ValidationError) -> str:
    errors = e.errors()
    if errors:
        msg = errors[0].get("msg", str(e))
        msg = re.sub(r"\s*\[type=.*\]$", "", msg)
        return msg
    return str(e)


_TYPE_MAP: dict[str, Any] = {
    "str": str,
    "int": int,
    "bool": bool,
    "float": float,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "SecretStr": str,
    "EmailStr": pydantic.EmailStr,
    "HttpUrl": pydantic.HttpUrl,
    "AnyUrl": pydantic.AnyUrl,
    "IPvAnyAddress": pydantic.IPvAnyAddress,
}

_OPTIONAL_PATTERN = re.compile(r"^Optional\[(.+)\]$")


def _resolve_type(annotation: str):
    base = annotation
    m = _OPTIONAL_PATTERN.match(annotation)
    if m:
        base = m.group(1)

    if base in _TYPE_MAP:
        return _TYPE_MAP[base]

    if base.startswith("list["):
        return list
    if base.startswith("set["):
        return set
    if base.startswith("dict["):
        return dict
    if base.startswith("tuple["):
        return tuple
    if base.startswith("Literal["):
        return str

    return None


def _validate_value(raw: str, annotation: str) -> tuple[bool, str | None, str | None]:
    if not raw.strip():
        if annotation.startswith("Optional["):
            return True, None, None
        return False, None, "Value is required"

    if annotation in ("str", "SecretStr", "Optional[str]", "Optional[SecretStr]"):
        return True, raw, None

    type_obj = _resolve_type(annotation)
    if type_obj is None:
        return True, raw, None

    adapter = pydantic.TypeAdapter(type_obj)

    try:
        adapter.validate_python(raw)
        return True, raw, None
    except pydantic.ValidationError:
        pass

    try:
        adapter.validate_json(raw)
        return True, raw, None
    except pydantic.ValidationError:
        pass

    try:
        parsed = ast.literal_eval(raw)
        adapter.validate_python(parsed)
        return True, raw, None
    except pydantic.ValidationError as e:
        return False, None, _pydantic_error_message(e)
    except (ValueError, SyntaxError):
        return False, None, _expected_format(annotation)


@app.command()
def init(
    env: Literal["dev", "prod"] = typer.Argument(help="Environment: dev or prod"),
) -> None:
    """Initialize config vars for the given environment."""
    try:
        project_root = ProjectStructure().root
    except RuntimeError:
        print_console.info("Not in a djdevx project. Run `ddx new` first.")
        return

    collector = SettingCollector(project_root)
    result = collector.collect()

    if not result.config_vars:
        print_console.info("No config vars declared in this project.")
        return

    if env == DEV:
        print_console.ok(
            "Configs ready: using built-in defaults. Create or edit .env to override defaults for local development."
        )
        return

    setup_readline()
    if env == PROD:
        resolve_source = resolve_config_source_prod
        env_prod_path = project_root / ".env.prod"
        prompted = 0
        skipped = 0

        for config_var in result.config_vars:
            key = config_var.name.upper()
            if resolve_source(config_var, project_root) != ConfigSource.MISSING:
                skipped += 1
                continue

            print_console.info(f"\n  Config var required: {config_var.name}")
            print_console.info(f"  Source: {config_var.source_file.name}")
            print_console.info(f"  Type: {config_var.type_annotation}")

            while True:
                value = input(f"  Enter value for {config_var.name}: ")
                is_valid, result_value, error = _validate_value(
                    value, config_var.type_annotation
                )
                if is_valid:
                    set_key(env_prod_path, key, result_value or "", quote_mode="always")
                    prompted += 1
                    break
                print_console.error(f"    Invalid: {error}")

        parts = []
        if prompted:
            parts.append(f"{prompted} from prompt")
        if skipped:
            parts.append(f"{skipped} already present (skipped)")

        summary = ", ".join(parts) if parts else "nothing to do"
        print_console.ok(f"Configs ready: {summary}.")


# ------ configs verify ------


_ENV_CONFIG_VERIFY: dict[str, dict[str, Any]] = {
    DEV: {
        "resolve_source": resolve_config_source_dev,
        "resolve_value": resolve_config_value_dev,
        "error_suffix": f" with no {DEV} default",
    },
    PROD: {
        "resolve_source": resolve_config_source_prod,
        "resolve_value": resolve_config_value_prod,
        "error_suffix": "",
        "fix_cmd": f"ddx settings configs init {PROD}",
    },
}


@app.command()
def verify(
    env: Literal["dev", "prod"] = typer.Argument(help="Environment: dev or prod"),
) -> None:
    """Verify config vars completeness."""
    try:
        project_root = ProjectStructure().root
    except RuntimeError:
        print_console.info("Not in a djdevx project. Run `ddx new` first.")
        raise typer.Exit(code=1)

    collector = SettingCollector(project_root)
    result = collector.collect()

    cfg = _ENV_CONFIG_VERIFY[env]
    missing: list[str] = []
    optional: list[str] = []
    for config_var in result.config_vars:
        source = cfg["resolve_source"](config_var, project_root)
        if source == ConfigSource.MISSING:
            missing.append(config_var.name)
        elif source == ConfigSource.CLASS_DEFAULT:
            optional.append(config_var.name)

    if optional:
        names = ", ".join(optional)
        print_console.info(
            f"{len(optional)} optional config var(s) using class defaults:"
        )
        print_console.info(f"  {names}")

    if missing:
        msg = f"{len(missing)} config var(s) missing{cfg['error_suffix']}:"
        print_console.error(msg)
        _print_configs_table(env, result, project_root, cfg)
        fix_cmd = cfg.get("fix_cmd")
        if fix_cmd:
            print_console.info(f"\nRun: {fix_cmd}")
        raise typer.Exit(code=1)

    total = len(result.config_vars)
    print_console.ok(f"All {total} config var(s) are present.")
