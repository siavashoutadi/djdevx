"""Styled questionary prompt wrappers — centralizes style so callers don't repeat it."""

from typing import Any

import questionary

_STYLE = questionary.Style(
    [
        ("qmark", "fg:ansigreen bold"),
        ("question", "bold"),
        ("answer", "fg:ansigreen bold"),
        ("pointer", "fg:ansiyellow bold"),
        ("highlighted", "fg:ansigreen bold"),
        ("selected", "fg:ansigreen"),
        ("separator", "fg:ansiblack"),
        ("instruction", ""),
        ("text", ""),
        ("disabled", "fg:ansiblack"),
    ]
)

Choice = questionary.Choice


def checkbox(message: str, choices: list[Any], **kwargs: Any) -> list[str] | None:
    return questionary.checkbox(message, choices=choices, style=_STYLE, **kwargs).ask()  # type: ignore[no-any-return]


def select(message: str, choices: list[Any], **kwargs: Any) -> str | None:
    return questionary.select(message, choices=choices, style=_STYLE, **kwargs).ask()  # type: ignore[no-any-return]


def confirm(message: str, default: bool = True, **kwargs: Any) -> bool | None:
    return questionary.confirm(message, default=default, style=_STYLE, **kwargs).ask()  # type: ignore[no-any-return]


def text(message: str, default: str = "", **kwargs: Any) -> str | None:
    return questionary.text(message, default=default, style=_STYLE, **kwargs).ask()  # type: ignore[no-any-return]


def password(message: str, default: str = "", **kwargs: Any) -> str | None:
    return questionary.password(message, default=default, style=_STYLE, **kwargs).ask()  # type: ignore[no-any-return]
