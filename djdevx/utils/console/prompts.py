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


def _normalize(message: str) -> str:
    """Ensure a prompt message ends with punctuation so the answer reads clearly."""
    message = message.rstrip()
    if message.endswith((":", "?")):
        return message
    return f"{message}:"


def checkbox(message: str, choices: list[Any], **kwargs: Any) -> list[str] | None:
    return questionary.checkbox(
        _normalize(message), choices=choices, style=_STYLE, **kwargs
    ).ask()  # type: ignore[no-any-return]


def select(message: str, choices: list[Any], **kwargs: Any) -> str | None:
    return questionary.select(
        _normalize(message), choices=choices, style=_STYLE, **kwargs
    ).ask()  # type: ignore[no-any-return]


def confirm(message: str, default: bool = True, **kwargs: Any) -> bool | None:
    return questionary.confirm(
        _normalize(message), default=default, style=_STYLE, **kwargs
    ).ask()  # type: ignore[no-any-return]


def text(message: str, default: str = "", **kwargs: Any) -> str | None:
    return questionary.text(
        _normalize(message), default=default, style=_STYLE, **kwargs
    ).ask()  # type: ignore[no-any-return]


def password(message: str, default: str = "", **kwargs: Any) -> str | None:
    return questionary.password(
        _normalize(message), default=default, style=_STYLE, **kwargs
    ).ask()  # type: ignore[no-any-return]
