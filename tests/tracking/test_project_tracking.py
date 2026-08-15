"""Unit tests for ProjectTracking section-scoped operations."""

import tomllib
from pathlib import Path

import pytest

from djdevx.utils.tracking import ProjectTracking, Section

SECTIONS = [Section.CACHE, Section.FEATURES, Section.DATABASE, Section.PACKAGES]


@pytest.fixture
def project(tmp_path: Path) -> ProjectTracking:
    """Return a ProjectTracking isolated to tmp_path with a djdevx.toml."""
    djdevx = tmp_path / "djdevx.toml"
    djdevx.write_text('project_name = "test"\n')
    return ProjectTracking(tmp_path)


@pytest.fixture(params=SECTIONS)
def section(request) -> str:
    """Parametrize over the sections ProjectTracking manages."""
    return request.param


# ── add ────────────────────────────────────────────────────────────────────────


class TestAdd:
    """Tests for ProjectTracking.add."""

    def test_add_creates_tracking_entry(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis")
        assert project.is_installed(section, "redis") is True

    def test_add_writes_to_djdevx_toml(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis")
        doc = tomllib.loads(project._djdevx_path.read_text())
        assert doc[section]["redis"]["display_name"] == "Redis"

    def test_add_idempotent(self, project: ProjectTracking, section: str) -> None:
        project.add(section, "redis", "Redis")
        project.add(section, "redis", "Redis")
        installed = project.list(section)
        assert list(installed.keys()).count("redis") == 1


# ── remove ─────────────────────────────────────────────────────────────────────


class TestRemove:
    """Tests for ProjectTracking.remove."""

    def test_remove_deletes_tracking_entry(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis")
        project.remove(section, "redis")
        assert project.is_installed(section, "redis") is False

    def test_remove_is_noop_when_not_installed(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.remove(section, "redis")  # should not raise

    def test_remove_only_affects_specified(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis")
        project.add(section, "memcached", "Memcached")
        project.remove(section, "redis")
        assert project.is_installed(section, "redis") is False
        assert project.is_installed(section, "memcached") is True


# ── is_installed ──────────────────────────────────────────────────────────────


class TestIsInstalled:
    """Tests for ProjectTracking.is_installed."""

    def test_returns_false_before_install(
        self, project: ProjectTracking, section: str
    ) -> None:
        assert project.is_installed(section, "redis") is False

    def test_returns_true_after_add(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis")
        assert project.is_installed(section, "redis") is True

    def test_returns_false_after_remove(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis")
        project.remove(section, "redis")
        assert project.is_installed(section, "redis") is False

    def test_unrelated_entries_are_independent(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis")
        assert project.is_installed(section, "redis") is True
        assert project.is_installed(section, "memcached") is False


# ── list ──────────────────────────────────────────────────────────────────────


class TestList:
    """Tests for ProjectTracking.list."""

    def test_empty_list(self, project: ProjectTracking, section: str) -> None:
        assert project.list(section) == {}

    def test_list_with_one_entry(self, project: ProjectTracking, section: str) -> None:
        project.add(section, "redis", "Redis")
        result = project.list(section)
        assert "redis" in result
        assert result["redis"]["display_name"] == "Redis"

    def test_list_with_multiple_entries(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis")
        project.add(section, "memcached", "Memcached")
        result = project.list(section)
        assert len(result) == 2
        assert "redis" in result
        assert "memcached" in result


# ── get_variants ──────────────────────────────────────────────────────────────


class TestGetVariants:
    """Tests for ProjectTracking.get_variants."""

    def test_empty_for_untracked(self, project: ProjectTracking, section: str) -> None:
        assert project.get_variants(section, "redis") == []

    def test_returns_added_variants(
        self, project: ProjectTracking, section: str
    ) -> None:
        project.add(section, "redis", "Redis", variants=["base", "mfa"])
        assert project.get_variants(section, "redis") == ["base", "mfa"]


# ── persistence ───────────────────────────────────────────────────────────────


class TestPersistence:
    """Tests for document load/save behavior."""

    def test_reads_do_not_create_section(self, tmp_path: Path) -> None:
        djdevx = tmp_path / "djdevx.toml"
        djdevx.write_text('project_name = "test"\n')
        project = ProjectTracking(tmp_path)
        assert project.is_installed(Section.CACHE, "redis") is False
        assert project.list(Section.CACHE) == {}
        doc = tomllib.loads(djdevx.read_text())
        assert "cache" not in doc

    def test_missing_djdevx_toml_creates_it(self, tmp_path: Path) -> None:
        project = ProjectTracking(tmp_path)
        project.add(Section.PACKAGES, "heroicons", "Heroicons")
        doc = tomllib.loads((tmp_path / "djdevx.toml").read_text())
        assert "heroicons" in doc["packages"]

    def test_sections_are_independent(self, tmp_path: Path) -> None:
        project = ProjectTracking(tmp_path)
        project.add(Section.CACHE, "redis", "Redis")
        project.add(Section.DATABASE, "postgres", "Postgres")
        assert project.is_installed(Section.CACHE, "redis") is True
        assert project.is_installed(Section.DATABASE, "redis") is False
        assert project.is_installed(Section.DATABASE, "postgres") is True
