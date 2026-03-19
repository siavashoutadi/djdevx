"""Unit tests for DjangoProjectManager."""

from djdevx.utils.django.project_manager import DjangoProjectManager


class TestHasDependency:
    """Tests for DjangoProjectManager.has_dependency – PEP 503 name normalization."""

    def _make_pm(
        self, dependencies: list[str], dev_deps: list[str] | None = None
    ) -> DjangoProjectManager:
        """Create a DjangoProjectManager instance with mocked pyproject.toml content."""
        pyproject_data = {
            "project": {"dependencies": dependencies},
            "dependency-groups": {"dev": dev_deps or []},
        }

        pm = object.__new__(DjangoProjectManager)

        def mock_get_deps(group: str = "") -> list[str]:
            if group:
                return pyproject_data.get("dependency-groups", {}).get(group, [])
            return pyproject_data.get("project", {}).get("dependencies", [])

        pm.get_dependencies = mock_get_deps  # type: ignore[method-assign]
        return pm

    # --- Exact match ---

    def test_exact_match_returns_true(self) -> None:
        pm = self._make_pm(["channels-redis>=4.0"])
        assert pm.has_dependency("channels-redis") is True

    def test_missing_returns_false(self) -> None:
        pm = self._make_pm(["channels-redis>=4.0"])
        assert pm.has_dependency("whitenoise") is False

    # --- Normalization: underscore vs hyphen ---

    def test_query_underscore_dep_hyphen(self) -> None:
        """Query with underscore matches dep recorded with hyphen (uv normalises on install)."""
        pm = self._make_pm(["channels-redis>=4.0"])
        assert pm.has_dependency("channels_redis") is True

    def test_query_hyphen_dep_underscore(self) -> None:
        """Query with hyphen matches dep recorded with underscore."""
        pm = self._make_pm(["channels_redis>=4.0"])
        assert pm.has_dependency("channels-redis") is True

    # --- Normalization: dots ---

    def test_dot_normalization(self) -> None:
        pm = self._make_pm(["zope.interface==6.0"])
        assert pm.has_dependency("zope-interface") is True

    # --- Extras are stripped from pyproject deps ---

    def test_dep_with_extras_still_matches(self) -> None:
        """channels[daphne] in pyproject → querying 'channels' matches."""
        pm = self._make_pm(["channels[daphne]>=4.0"])
        assert pm.has_dependency("channels") is True

    # --- Dev group ---

    def test_dev_group_underscore_matches_hyphen(self) -> None:
        pm = self._make_pm([], ["twisted-http2>=1.0"])
        assert pm.has_dependency("twisted_http2", group="dev") is True

    def test_dev_group_not_found_in_main(self) -> None:
        pm = self._make_pm(["channels-redis>=4.0"], [])
        assert pm.has_dependency("channels-redis", group="dev") is False

    # --- Case insensitivity ---

    def test_case_insensitive_match(self) -> None:
        pm = self._make_pm(["Django>=4.2"])
        assert pm.has_dependency("django") is True
