"""Tests for profile batch installer — answer resolution and dispatch."""

from unittest.mock import patch

from djdevx.profiles.installer import _resolve_answers_for, install_profile
from djdevx.profiles.models import AnswersFile, Profile, ProfileInstallable


class TestResolveAnswersFor:
    def test_none_answers(self):
        assert _resolve_answers_for(None, "packages", "whitenoise", []) == {}

    def test_missing_installable(self):
        answers = AnswersFile(packages={"whitenoise": {"secret": "x"}})
        assert _resolve_answers_for(answers, "packages", "nope", []) == {}

    def test_flat_params(self):
        answers = AnswersFile(features={"pwa": {"app_name": "X", "short_name": "Y"}})
        result = _resolve_answers_for(answers, "features", "pwa", [])
        assert result == {"app_name": "X", "short_name": "Y"}

    def test_variant_nested_params(self):
        answers = AnswersFile(
            packages={
                "django-allauth": {
                    "account": {"email_subject_prefix": "[X] "},
                    "mfa": {"enable_totp": True},
                }
            }
        )
        result = _resolve_answers_for(
            answers, "packages", "django-allauth", ["account", "mfa"]
        )
        assert result == {"email_subject_prefix": "[X] ", "enable_totp": True}

    def test_variant_nested_only_selected(self):
        answers = AnswersFile(
            packages={
                "django-allauth": {
                    "account": {"email_subject_prefix": "[X] "},
                    "mfa": {"enable_totp": True},
                }
            }
        )
        result = _resolve_answers_for(answers, "packages", "django-allauth", ["mfa"])
        assert result == {"enable_totp": True}

    def test_ignores_non_dict_entry(self):
        answers = AnswersFile(packages={"whitenoise": "not-a-table"})
        assert _resolve_answers_for(answers, "packages", "whitenoise", []) == {}


class TestInstallProfile:
    def test_installs_all_sections(self):
        profile = Profile(
            packages={"whitenoise": ProfileInstallable()},
            features={},
            frameworks={},
            database={"postgres": ProfileInstallable()},
            cache={"redis": ProfileInstallable()},
        )

        calls = []

        def fake_add(
            cls,
            name,
            provider=None,
            verbose=False,
            is_multi=False,
            answers=None,
            variants=None,
        ):
            calls.append(name)
            return True

        class FakeRegistry:
            def get(self, name):
                return FakeCls()

            def names(self):
                return []

        class FakeCls:
            pass

        def fake_registry_for(section_key):
            return FakeRegistry()

        with (
            patch("djdevx.profiles.installer.add_installable", fake_add),
            patch("djdevx.profiles.installer._registry_for", fake_registry_for),
            patch("djdevx.profiles.installer._ensure_registries"),
        ):
            install_profile(profile)

        assert calls == ["whitenoise", "postgres", "redis"]

    def test_unknown_installable_skipped(self):
        profile = Profile(packages={"nope": ProfileInstallable()})

        with (
            patch("djdevx.profiles.installer.add_installable") as add,
            patch(
                "djdevx.profiles.installer._registry_for", side_effect=KeyError("nope")
            ),
            patch("djdevx.profiles.installer._ensure_registries"),
        ):
            result_ok = install_profile(profile)

        add.assert_not_called()
        assert result_ok is None

    def test_provider_and_variants_passed_through(self):
        profile = Profile(
            packages={
                "django-anymail": ProfileInstallable(variant="mailgun"),
                "django-allauth": ProfileInstallable(variants=["mfa"]),
            }
        )

        calls = []

        def fake_add(
            cls,
            name,
            provider=None,
            verbose=False,
            is_multi=False,
            answers=None,
            variants=None,
        ):
            calls.append((name, provider, variants))
            return True

        class FakeRegistry:
            def get(self, name):
                return FakeCls()

            def names(self):
                return []

        class FakeCls:
            pass

        with (
            patch("djdevx.profiles.installer.add_installable", fake_add),
            patch("djdevx.profiles.installer._registry_for", lambda _k: FakeRegistry()),
            patch("djdevx.profiles.installer._ensure_registries"),
        ):
            install_profile(profile)

        assert calls == [
            ("django-anymail", "mailgun", None),
            ("django-allauth", None, ["mfa"]),
        ]

    def test_answers_resolved_and_passed(self):
        profile = Profile(features={"pwa": ProfileInstallable()})
        answers = AnswersFile(features={"pwa": {"app_name": "X"}})

        captured = {}

        def fake_add(
            cls,
            name,
            provider=None,
            verbose=False,
            is_multi=False,
            answers=None,
            variants=None,
        ):
            captured["answers"] = answers
            return True

        class FakeRegistry:
            def get(self, name):
                return FakeCls()

            def names(self):
                return []

        class FakeCls:
            pass

        with (
            patch("djdevx.profiles.installer.add_installable", fake_add),
            patch("djdevx.profiles.installer._registry_for", lambda _k: FakeRegistry()),
            patch("djdevx.profiles.installer._ensure_registries"),
        ):
            install_profile(profile, answers=answers)

        assert captured["answers"] == {"app_name": "X"}
