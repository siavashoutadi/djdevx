"""Tests for profile/answer loading — local files, URLs, git repos, builtins."""

import pytest

from djdevx.profiles.loader import (
    autocomplete_profile,
    list_builtin_profiles,
    load_answers,
    load_profile,
    resolve_builtin,
    resolve_source,
)


class TestAutocompleteProfile:
    def test_suggests_builtins_when_empty(self):
        assert autocomplete_profile("") == ["multi-page"]

    def test_filters_by_prefix(self):
        assert autocomplete_profile("m") == ["multi-page"]
        assert autocomplete_profile("multi") == ["multi-page"]
        assert autocomplete_profile("api") == []


class TestBuiltinProfiles:
    def test_list_builtin(self):
        names = list_builtin_profiles()
        assert "multi-page" in names

    def test_resolve_builtin(self):
        path = resolve_builtin("multi-page")
        assert path.exists()
        assert path.suffix == ".toml"

    def test_resolve_builtin_unknown(self):
        with pytest.raises(FileNotFoundError):
            resolve_builtin("does-not-exist")

    def test_load_builtin_profile(self):
        profile = load_profile(resolve_builtin("multi-page"))
        assert "django-htmx" in profile.packages
        assert "starting-point-ui" in profile.frameworks
        assert "postgres" in profile.database
        assert "redis" in profile.cache


class TestLocalFiles:
    def test_resolve_local_path(self, temp_dir):
        f = temp_dir / "profile.toml"
        f.write_text("[new]\npython_version = '3.14'\n")
        resolved = resolve_source(str(f))
        assert resolved == f

    def test_resolve_missing_path(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            resolve_source(str(temp_dir / "nope.toml"))

    def test_load_profile(self, temp_dir):
        f = temp_dir / "profile.toml"
        f.write_text("[packages]\nwhitenoise = {}\n")
        profile = load_profile(f)
        assert profile.packages["whitenoise"].variants is None

    def test_load_profile_missing(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            load_profile(temp_dir / "missing.toml")

    def test_load_answers(self, temp_dir):
        f = temp_dir / "answers.toml"
        f.write_text("[features.pwa]\napp_name = 'X'\n")
        answers = load_answers(f)
        assert answers.features["pwa"]["app_name"] == "X"


class TestUrls:
    def test_resolve_http_url(self, monkeypatch):
        class FakeResponse:
            text = "[new]\npython_version = '3.14'\n"

            def raise_for_status(self):
                return None

        def fake_get(url, timeout):
            assert url.startswith("https://")
            return FakeResponse()

        monkeypatch.setattr("djdevx.profiles.loader.requests.get", fake_get)
        path = resolve_source("https://example.com/profiles/api.toml")
        assert path.exists()
        assert "python_version" in path.read_text()


class TestGitRepos:
    def test_git_pattern_resolves_shallow_clone(self, monkeypatch):
        calls = {}

        import subprocess as sp

        def fake_clone(args, capture_output, text):
            calls["url"] = args[-2]
            return sp.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

        def fake_mkdtemp(prefix):
            calls["prefix"] = prefix
            return "/tmp/ddx-profile-fake"

        monkeypatch.setattr("djdevx.profiles.loader.subprocess.run", fake_clone)
        monkeypatch.setattr("djdevx.profiles.loader.tempfile.mkdtemp", fake_mkdtemp)
        monkeypatch.setattr(
            "djdevx.profiles.loader.Path.exists",
            lambda self, *a: str(self).endswith("api.toml"),
        )

        source = "https://github.com/user/repo.git@profiles/api.toml"
        path = resolve_source(source)
        assert calls["url"] == "https://github.com/user/repo.git"
        assert str(path).endswith("profiles/api.toml")
