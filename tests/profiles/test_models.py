"""Tests for profile and answer file models."""

import pytest
from pydantic import ValidationError

from djdevx.profiles.models import AnswersFile, Profile, ProfileInstallable


class TestProfileInstallable:
    def test_empty_defaults(self):
        entry = ProfileInstallable()
        assert entry.variant is None
        assert entry.variants is None

    def test_exclusive_variant(self):
        entry = ProfileInstallable(variant="mailgun")
        assert entry.variant == "mailgun"
        assert entry.variants is None

    def test_additive_variants(self):
        entry = ProfileInstallable(variants=["account", "mfa"])
        assert entry.variants == ["account", "mfa"]

    def test_rejects_unknown_field(self):
        with pytest.raises(ValidationError):
            ProfileInstallable(bogus="x")  # type: ignore[call-arg]


class TestProfile:
    def test_empty_profile(self):
        profile = Profile()
        assert profile.packages == {}
        assert profile.features == {}
        assert profile.frameworks == {}
        assert profile.database == {}
        assert profile.cache == {}

    def test_parse_toml_dict(self):
        data = {
            "new": {"python_version": "3.14", "git_init": False},
            "packages": {"whitenoise": {}, "django-allauth": {"variants": ["account"]}},
            "database": {"postgres": {}},
            "cache": {"redis": {}},
        }
        profile = Profile.model_validate(data)
        assert profile.new.python_version == "3.14"
        assert profile.new.git_init is False
        assert set(profile.packages) == {"whitenoise", "django-allauth"}
        assert profile.packages["django-allauth"].variants == ["account"]
        assert profile.database["postgres"].variants is None

    def test_accepts_unknown_toml_sections(self):
        data = {"bogus": {"x": {}}}
        profile = Profile.model_validate(data)
        assert profile.packages == {}


class TestAnswersFile:
    def test_empty(self):
        answers = AnswersFile()
        assert answers.packages == {}

    def test_variant_nested_params(self):
        data = {
            "packages": {
                "django-allauth": {
                    "account": {"email_subject_prefix": "[X] - "},
                    "mfa": {"enable_totp": True},
                }
            }
        }
        answers = AnswersFile.model_validate(data)
        assert answers.packages["django-allauth"]["account"] == {
            "email_subject_prefix": "[X] - "
        }

    def test_flat_params(self):
        data = {"features": {"pwa": {"app_name": "My App", "short_name": "MyApp"}}}
        answers = AnswersFile.model_validate(data)
        assert answers.features["pwa"]["app_name"] == "My App"
