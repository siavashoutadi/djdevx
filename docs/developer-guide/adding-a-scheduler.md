# Adding a Scheduler

Step-by-step guide to adding a new scheduler provider to djdevx. Schedulers
trigger time-based work (Celery Beat) and depend on a task queue. Only **one**
scheduler can be installed at a time — same constraint as databases, caches,
and task queues.

This page focuses on scheduler-specific concerns. Shared concepts (variants,
install params, secrets, hooks, templates, testing) live in
[Common Concepts](creating-an-installable.md).

## Table of Contents

1. [Scheduler pattern](#scheduler-pattern)
2. [Templates directory](#templates-directory)
3. [Dependency on a task queue](#dependency-on-a-task-queue)
4. [Native dev service](#native-dev-service)
5. [CLI commands](#cli-commands)
6. [Testing](#testing)

---

## Scheduler pattern

Identical to the task-queue pattern, with `needs` pointing back at the
task-queue provider:

```python
# djdevx/providers/scheduler/celery_beat/__init__.py
from .._base import BaseScheduler
from .._registry import register
from ....installable.models import TASK_QUEUE, InstallableRef
from ....utils.devcontainer import DockerComposeManager, ServiceConfig
from ....utils.types.pixi_types import PixiPackageSpec

CELERY_BEAT_DOCKER_SERVICE: ServiceConfig = {
    "name": "celery-beat",
    "build": {"context": ".", "dockerfile": "Dockerfile"},
    "volumes": ["../:/home/devuser/workspace:cached"],
    "environment": {"DEVCONTAINER": "true"},
    "networks": ["devcontainer"],
    "depends_on": ["cache", "celery-worker", "devcontainer"],
    "command": "/home/devuser/.pixi/bin/pixi run celery -A applications.celery beat --loglevel=info",
}


@register
class CeleryBeatScheduler(BaseScheduler):
    name: str = "celery-beat"
    display_name: str = "Celery Beat"
    description: str = "Celery Beat — database-backed periodic task scheduler"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-celery-beat", kind="pypi")
    ]
    needs: list[InstallableRef] = [InstallableRef("celery", TASK_QUEUE)]

    def after_pixi_install(self) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.add_service(CELERY_BEAT_DOCKER_SERVICE, [])

    def after_pixi_remove(self) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.remove_service(CELERY_BEAT_DOCKER_SERVICE, [])
```

## Templates directory

```
djdevx/providers/scheduler/celery_beat/
├── __init__.py
└── templates/
    └── settings/
        ├── apps/
        │   └── celery.py            # → settings/apps/celery.py
        └── django/
            └── celery_beat.py       # → settings/django/celery_beat.py
```

The `apps/` file appends `django_celery_beat` to `INSTALLED_APPS`; because the
settings loader executes `settings/django/` before `settings/apps/`, the import
of `INSTALLED_APPS` from `settings.django.base` resolves correctly.

The `django/` file switches to the database scheduler:

```python
CELERY_BEAT_SCHEDULER: str = "django_celery_beat.schedulers:DatabaseScheduler"
```

## Dependency on a task queue

Schedulers declare their task-queue provider via `needs`, so
`ddx scheduler add celery-beat` auto-installs Celery first. Removing the
scheduler leaves the task queue and broker cache in place.

## Native dev service

Register a `CeleryBeatService` daemon in `services/celery.py` (category
`scheduler`, portless pid daemon). The scheduler requires the worker to be up
first — `ddx dev start` orders cache → worker → beat.

## CLI commands

```
ddx scheduler add [NAME] [-v]
ddx scheduler remove [NAME] [-v]
ddx scheduler list
```

## Testing

```bash
ddx scheduler add celery-beat
ddx scheduler list
ddx scheduler remove celery-beat
```

The CLI integration tests (`tests/scheduler/test_celery_beat.py`) verify the
auto-installed task queue (`needs`), the `django-celery-beat` dependency, both
settings files, the compose beat service, and that removal keeps the task queue.

## Related

- [Common Concepts](creating-an-installable.md) — shared pattern, variants, params, hooks, templates
- [Scheduler Architecture](scheduler-architecture.md) — BaseScheduler details
- [Adding a Task Queue](adding-a-task-queue.md) — producer pattern this depends on
- [Installable System](installable-system.md) — Shared infrastructure
