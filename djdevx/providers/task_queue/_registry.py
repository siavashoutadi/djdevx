"""Task-queue registry — TASK_QUEUE_REGISTRY dict and register decorator."""

from ...installable.registry import Registry
from ...installable.models import TASK_QUEUE
from ._base import BaseTaskQueue

TASK_QUEUE_REGISTRY: Registry[BaseTaskQueue] = Registry(TASK_QUEUE)
register = TASK_QUEUE_REGISTRY.register
get_task_queue = TASK_QUEUE_REGISTRY.get
list_task_queues = TASK_QUEUE_REGISTRY.names
