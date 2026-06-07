"""
configs init — populates .env.prod for production config vars.
"""

import ast
import re
from typing import Any, Optional

import pydantic
import typer

from .....utils.console.print import print_console
from dotenv import set_key

from .....utils.djdevx_config.backend.django import DjangoConfig
from .....utils.django.setting_collector import SettingCollector
from .._source import ConfigSource, resolve_config_source_prod

app = typer.Typer(no_args_is_help=True)


_TYPE_HINTS: dict[str, str] = {
    "bool": "true/false, yes/no, or 1/0",
    "int": "an integer",
    "float": "a number",
    "EmailStr": "a valid email address, e.g. user@example.com",
}


def _expected_format(annotation: str) -> str:
    """Return a user-friendly expected-format hint for the annotation."""
    base = _expected_format_base(annotation)
    return f"Expected {base}"


def _expected_format_base(annotation: str) -> str:
    # Known simple types (bool, int, float, EmailStr, etc.)
    # Example: "bool" -> "true/false, yes/no, or 1/0"
    if annotation in _TYPE_HINTS:
        return _TYPE_HINTS[annotation]

    # Literal["a", "b", "c"] -> list the allowed values
    # Example: Literal["dev", "prod"] -> 'one of: "dev", "prod"'
    if annotation.startswith("Literal["):
        return f"one of: {annotation[8:-1]}"

    # Optional[X] -> X's hint with "or leave empty to skip" appended
    # Example: Optional[EmailStr] -> "a valid email address, e.g. user@example.com (or leave empty to skip)"
    if annotation.startswith("Optional["):
        inner = annotation[9:-1]
        return f"{_expected_format_base(inner)} (or leave empty to skip)"

    # List / dict / set generics -> user must supply JSON syntax
    # Example: list[str] -> 'a JSON value, e.g. ["item1", "item2"] or {"key": "value"}'
    if (
        annotation.startswith("list[")
        or annotation.startswith("dict[")
        or annotation.startswith("set[")
    ):
        return 'a JSON value, e.g. ["item1", "item2"] or {"key": "value"}'

    # Fallback for unrecognised annotations (HttpUrl, IPvAnyAddress, etc.)
    return "a valid value"


def _pydantic_error_message(e: pydantic.ValidationError) -> str:
    """Extract the first actionable error message from a ValidationError."""
    errors = e.errors()
    if errors:
        msg = errors[0].get("msg", str(e))
        # Remove the type suffix like "[type=..., input_value=..., input_type=...]"
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

# Matches "Optional[str]", "Optional[EmailStr]", etc. and captures the inner type.
# Used in _resolve_type() to detect optional annotations so the inner type can be
# extracted and looked up in the type map.
_OPTIONAL_PATTERN = re.compile(r"^Optional\[(.+)\]$")


def _resolve_type(annotation: str):
    """Resolve annotation string to type object, or None if unknown.

    Uses a fixed lookup dict instead of eval() for safety.
    Handles common type annotations including Optional[X],
    list[X], dict[K, V], etc.
    """
    base = annotation
    is_optional = False
    m = _OPTIONAL_PATTERN.match(annotation)
    if m:
        base = m.group(1)
        is_optional = True

    if base in _TYPE_MAP:
        return _TYPE_MAP[base]

    # Generics like list[str], dict[str, int], etc.
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

    if is_optional and base in _TYPE_MAP:
        return Optional[_TYPE_MAP[base]]  # type: ignore[assignment]

    return None


def validate_value(raw: str, annotation: str) -> tuple[bool, str | None, str | None]:
    """Validate a raw input string against the pydantic type annotation.

    Returns (is_valid, canonical_value, error_message).
    """

    # 1. Empty input — only valid for Optional[X] fields (stored as None).
    #    Otherwise return "Value is required".
    if not raw.strip():
        if annotation.startswith("Optional["):
            return True, None, None
        return False, None, "Value is required"

    # 2. Short-circuit for strings — str and SecretStr (including optional
    #    variants) accept any raw text. No pydantic validation needed.
    if annotation in ("str", "SecretStr", "Optional[str]", "Optional[SecretStr]"):
        return True, raw, None

    # 3. Resolve annotation string (e.g. "int", "Literal['a','b']") to a Python
    #    type object via the safe lookup dict. If the type is unknown, accept
    #    the value as-is.
    type_obj = _resolve_type(annotation)
    if type_obj is None:
        return True, raw, None

    # 4. Validate with pydantic TypeAdapter using three attempts:
    adapter = pydantic.TypeAdapter(type_obj)

    #    a) validate_python(raw) — treat the raw string as the actual value.
    #       Works for int, float, bool (e.g. "True" parses as Python bool).
    try:
        adapter.validate_python(raw)
        return True, raw, None
    except pydantic.ValidationError:
        pass

    #    b) validate_json(raw) — parse the string as JSON first.
    #       Catches cases like JSON arrays or quoted strings.
    try:
        adapter.validate_json(raw)
        return True, raw, None
    except pydantic.ValidationError:
        pass

    #    c) ast.literal_eval(raw) — safely evaluate Python literals (e.g.
    #       ["a", "b"] as a list), then validate the parsed value.
    try:
        parsed = ast.literal_eval(raw)
        adapter.validate_python(parsed)
        return True, raw, None
    except pydantic.ValidationError as e:
        return False, None, _pydantic_error_message(e)
    except (ValueError, SyntaxError):
        return False, None, _expected_format(annotation)


@app.command("prod")
def init_prod() -> None:
    """
    Initialise .env.prod with required config variables.

    For each config var without a prod default, prompts the user for a value
    and writes it to .env.prod in KEY=VALUE format. Idempotent — skips
    keys that already exist in .env.prod.
    """
    config = DjangoConfig()
    backend_root = config.django_backend_root
    collector = SettingCollector(backend_root)
    result = collector.collect()

    if not result.config_vars:
        print_console.info("No config vars declared in this project.")
        return

    env_prod_path = backend_root / ".env.prod"
    prompted = 0
    skipped = 0

    for config_var in result.config_vars:
        key = config_var.name.upper()
        if resolve_config_source_prod(config_var, backend_root) != ConfigSource.MISSING:
            skipped += 1
            continue

        print_console.info(f"\n  Config var required: {config_var.name}")
        print_console.info(f"  Source: {config_var.source_file.name}")
        print_console.info(f"  Type: {config_var.type_annotation}")

        while True:
            value = input(f"  Enter value for {config_var.name}: ")
            is_valid, result_value, error = validate_value(
                value, config_var.type_annotation
            )
            if is_valid:
                set_key(
                    env_prod_path,
                    key,
                    result_value or "",
                    quote_mode="always",
                )
                prompted += 1
                break
            print_console.error(f"    Invalid: {error}")

    parts = []
    if prompted:
        parts.append(f"{prompted} from prompt")
    if skipped:
        parts.append(f"{skipped} already present (skipped)")

    summary = ", ".join(parts) if parts else "nothing to do"
    print_console.success(f"\nConfigs ready: {summary}.")
