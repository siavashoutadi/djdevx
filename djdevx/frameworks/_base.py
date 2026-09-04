"""BaseFramework — thin alias over the single Provider for the frameworks domain.

Wires the CSS/JS framework behavior (:class:`CSSFrameworkProviderMixin`) onto the
single :class:`Provider`. Kept for backward compatibility so existing provider
payloads and tests that ``from .._base import BaseFramework`` keep working;
removed in a later phase.
"""

from ..provider import FRAMEWORK_KIND, CSSFrameworkProviderMixin, Provider


class BaseFramework(CSSFrameworkProviderMixin, Provider):
    """Base class for CSS/JS frameworks."""

    kind = FRAMEWORK_KIND
