"""Scheduler CLI — add/remove/list schedulers with auto-discovery."""

from ...cli.factory import domain_app
from ._base import BaseScheduler
from ._registry import SCHEDULER_REGISTRY

app = domain_app(
    BaseScheduler,
    label="Scheduler",
    registry=SCHEDULER_REGISTRY,
    discover_path=__path__,
    discover_name=__name__,
    single=True,
)
