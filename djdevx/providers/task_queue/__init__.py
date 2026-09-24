"""Task-queue CLI — add/remove/list task-queues with auto-discovery."""

from ...cli.factory import domain_app
from ._base import BaseTaskQueue
from ._registry import TASK_QUEUE_REGISTRY

app = domain_app(
    BaseTaskQueue,
    label="Task Queue",
    registry=TASK_QUEUE_REGISTRY,
    discover_path=__path__,
    discover_name=__name__,
    single=True,
)
