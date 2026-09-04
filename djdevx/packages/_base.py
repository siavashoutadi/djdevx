"""BasePackage — thin alias over the single Provider for the packages domain.

Kept for backward compatibility so existing provider payloads and tests that
``from .._base import BasePackage`` keep working; removed in a later phase.
"""

from ..provider import PACKAGE_KIND, Provider


class BasePackage(Provider):
    """Base class for Django packages."""

    kind = PACKAGE_KIND
