"""Tests for prompt message normalization."""

from djdevx.utils.console.prompts import _normalize


def test_normalize_appends_colon_when_missing():
    assert (
        _normalize("Please enter the display name") == "Please enter the display name:"
    )


def test_normalize_keeps_existing_colon():
    assert _normalize("Project name:") == "Project name:"


def test_normalize_keeps_existing_question_mark():
    assert _normalize("Which provider do you want to use?") == (
        "Which provider do you want to use?"
    )


def test_normalize_strips_trailing_whitespace():
    assert _normalize("Scope   ") == "Scope:"
