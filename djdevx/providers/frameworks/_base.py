"""BaseFramework — generic framework base (plus CSSFramework for CSS/JS frameworks).

``BaseFramework`` is a thin alias over the single :class:`Provider` for the
frameworks domain and carries no CSS/JS assumptions, so the domain can host any
kind of framework (CSS/JS bundles, Tailwind tooling, etc.).

``CSSFramework`` layers the CSS/JS vendor-download behavior (via
:class:`~djdevx.provider.CSSFrameworkProviderMixin`) on top for frameworks that
ship pre-built CSS/JavaScript assets. Its data fields are declared here as
pydantic model fields so framework subclasses override them silently (no pydantic
shadow-attribute warnings).

Kept for backward compatibility so existing provider payloads and tests that
``from .._base import X`` keep working; removed in a later phase.
"""

from ...provider import FRAMEWORK_KIND, CSSFrameworkProviderMixin, Provider


class BaseFramework(Provider):
    """Base class for all frameworks (not limited to CSS/JS)."""

    kind = FRAMEWORK_KIND

    @property
    def _base_template_path(self):
        """Path to the project's base template (framework-agnostic helper)."""
        return self.structure.base_template


class CSSFramework(CSSFrameworkProviderMixin, BaseFramework):
    """Base class for CSS/JS frameworks that download vendored assets."""

    css_url: str = ""
    css_filename: str = ""
    js_url: str = ""
    js_filename: str = ""
    js_module: bool = False
