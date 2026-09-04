"""BaseFeature — thin alias over the single Provider for the features domain.

Kept for backward compatibility so existing provider payloads and tests that
``from .._base import BaseFeature`` keep working; removed in a later phase.
"""

from ...provider import FEATURE_KIND, Provider


class BaseFeature(Provider):
    """Base class for Django features."""

    kind = FEATURE_KIND
