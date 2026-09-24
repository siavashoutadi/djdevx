"""BaseScheduler — thin alias over the single Provider for the scheduler domain.

Kept consistent with the database/cache domain base classes: providers
declare ``kind`` and the section is derived automatically.
"""

from ...provider import SCHEDULER_KIND, Provider


class BaseScheduler(Provider):
    """Base class for scheduler (time-based trigger) providers."""

    kind = SCHEDULER_KIND
