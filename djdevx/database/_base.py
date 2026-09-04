"""BaseDatabase — thin alias over the single Provider for the database domain.

Kept for backward compatibility so existing provider payloads and tests that
``from .._base import BaseDatabase`` keep working; removed in a later phase.
"""

from ..provider import DATABASE_KIND, Provider


class BaseDatabase(Provider):
    """Base class for database providers."""

    kind = DATABASE_KIND
