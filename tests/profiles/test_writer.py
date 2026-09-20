"""Tests for the profile generator/writer logic."""

from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from tomlkit import parse

from djdevx.profiles.writer import (
    create_profile_interactive,
    generate_profile_from_project,
    write_answers_toml,
    write_profile_toml,
)
from djdevx.profiles.models import Profile, ProfileInstallable


def _write_djdevx_toml(project_root: Path) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "djdevx.toml").write_text(
        "project_name = 'myproject'\n"
        "[packages]\n"
        "[packages.whitenoise]\n"
        "installed = true\n"
        "[features]\n"
        "[frameworks]\n"
        "[database]\n"
        "[database.postgres]\n"
        "installed = true\n"
        "[cache]\n"
        "[cache.redis]\n"
        "installed = true\n"
    )


class TestGenerateFromProject:
    def test_generates_profile_with_installed(self, temp_dir):
        _write_djdevx_toml(temp_dir)
        profile = generate_profile_from_project(temp_dir)

        assert "whitenoise" in profile.packages
        assert "postgres" in profile.database
        assert "redis" in profile.cache
        assert profile.packages["whitenoise"].variant is None

    def test_captures_variants(self, temp_dir):
        (temp_dir / "djdevx.toml").write_text(
            "project_name = 'x'\n"
            "[packages]\n"
            "[packages.django-allauth]\n"
            "installed = true\n"
            "variants = ['account', 'mfa']\n"
            "[packages.django-anymail]\n"
            "installed = true\n"
            "variant = 'mailgun'\n"
        )
        profile = generate_profile_from_project(temp_dir)
        assert profile.packages["django-allauth"].variants == ["account", "mfa"]
        assert profile.packages["django-anymail"].variant == "mailgun"

    def test_empty_project(self, temp_dir):
        profile = generate_profile_from_project(temp_dir)
        assert profile.packages == {}
        assert profile.database == {}


class TestWriteToml:
    def test_write_profile_roundtrip(self, temp_dir):
        profile = Profile(
            new={},
            packages={
                "whitenoise": ProfileInstallable(),
                "django-allauth": ProfileInstallable(variants=["account"]),
                "django-anymail": ProfileInstallable(variant="mailgun"),
            },
        )
        out = temp_dir / "profile.toml"
        write_profile_toml(profile, out)

        data = parse(out.read_text())
        assert "whitenoise" in data["packages"]
        assert data["packages"]["django-allauth"]["variants"] == ["account"]
        assert data["packages"]["django-anymail"]["variant"] == "mailgun"

    def test_write_profile_uses_inline_entries(self, temp_dir):
        profile = Profile(
            packages={"whitenoise": ProfileInstallable()},
        )
        out = temp_dir / "profile.toml"
        write_profile_toml(profile, out)

        text = out.read_text()
        assert "[packages]" in text
        assert "whitenoise = {}" in text
        assert "[packages.whitenoise]" not in text

    def test_write_answers_roundtrip(self, temp_dir):
        answers = {
            "packages": {
                "django-allauth": {"mfa": {"enable_totp": True}},
                "whitenoise": {"secret": "abc"},
            }
        }
        out = temp_dir / "answers.toml"
        write_answers_toml(answers, out)

        data = parse(out.read_text())
        assert data["packages"]["django-allauth"]["mfa"]["enable_totp"] is True
        assert data["packages"]["whitenoise"]["secret"] == "abc"


class TestCancelAborts:
    def test_cancel_on_section_selection_aborts(self):
        with patch("djdevx.profiles.writer.prompts.checkbox", return_value=None):
            with pytest.raises(typer.Abort):
                create_profile_interactive()

    def test_cancel_on_param_prompt_aborts(self):
        from djdevx.profiles.writer import _collect_param_answers
        from djdevx.installable.models import InstallParam

        installable = type(
            "Stub",
            (),
            {"install_params": [InstallParam(name="secret", prompt="Secret")]},
        )()
        with patch("djdevx.profiles.writer.prompts.text", return_value=None):
            with pytest.raises(typer.Abort):
                _collect_param_answers(installable, "stub", {})
