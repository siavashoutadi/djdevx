"""BaseCache — thin alias over the single Provider for the cache domain.

Kept for backward compatibility so existing provider payloads and tests that
``from .._base import BaseCache`` keep working; removed in a later phase.
"""

from ...provider import CACHE_KIND, Provider


class BaseCache(Provider):
    """Base class for cache backends."""

    kind = CACHE_KIND
