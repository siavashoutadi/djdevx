"""Scheduler registry — SCHEDULER_REGISTRY dict and register decorator."""

from ...installable.registry import Registry
from ...installable.models import SCHEDULER
from ._base import BaseScheduler

SCHEDULER_REGISTRY: Registry[BaseScheduler] = Registry(SCHEDULER)
register = SCHEDULER_REGISTRY.register
get_scheduler = SCHEDULER_REGISTRY.get
list_schedulers = SCHEDULER_REGISTRY.names
