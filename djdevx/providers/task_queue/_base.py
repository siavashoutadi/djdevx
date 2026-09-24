"""BaseTaskQueue — thin alias over the single Provider for the task-queue domain.

Kept consistent with the database/cache domain base classes: providers
declare ``kind`` and the section is derived automatically.
"""

from ...provider import TASK_QUEUE_KIND, Provider


class BaseTaskQueue(Provider):
    """Base class for task-queue (background worker) providers."""

    kind = TASK_QUEUE_KIND
