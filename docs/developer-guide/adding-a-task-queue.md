# Adding a Task Queue

Step-by-step guide to adding a new task-queue provider to djdevx. Task queues
manage async-work providers (Celery) with Docker Compose integration and
`needs`-based broker setup. Only **one** task queue can be installed at a time —
same constraint as databases and caches.

This page focuses on task-queue-specific concerns. Shared concepts (variants,
install params, secrets, hooks, templates, testing) live in
[Common Concepts](creating-an-installable.md).

## Table of Contents

1. [Task-queue pattern](#task-queue-pattern)
2. [Templates directory](#templates-directory)
3. [Broker via needs](#broker-via-needs)
4. [Devcontainer worker service](#devcontainer-worker-service)
5. [Native dev service](#native-dev-service)
6. [Single-instance constraint](#single-instance-constraint)
7. [CLI commands](#cli-commands)
8. [Testing](#testing)

---

## Task-queue pattern

The same hook-based approach as databases/caches: `after_pixi_install()` /
`after_pixi_remove()` manage the Docker Compose worker service, plus a
`needs` entry that auto-installs the broker cache:

```python
# djdevx/providers/task_queue/celery/__init__.py
from .._base import BaseTaskQueue
from .._registry import register
from ....installable.models import CACHE, InstallableRef
from ....utils.devcontainer import DockerComposeManager, ServiceConfig
from ....utils.types.pixi_types import PixiPackageSpec

CELERY_WORKER_DOCKER_SERVICE: ServiceConfig = {
    "name": "celery-worker",
    "build": {"context": ".", "dockerfile": "Dockerfile"},
    "volumes": ["../:/home/devuser/workspace:cached"],
    "environment": {"DEVCONTAINER": "true"},
    "networks": ["devcontainer"],
    "depends_on": ["cache", "devcontainer"],
    "command": "/home/devuser/.pixi/bin/pixi run celery -A applications.celery worker --loglevel=info",
}


@register
class CeleryTaskQueue(BaseTaskQueue):
    name: str = "celery"
    display_name: str = "Celery"
    description: str = "Celery distributed task queue"
    # The Redis client ships with the auto-installed cache, so only the app
    # package is declared here.
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("celery", kind="pypi")]
    needs: list[InstallableRef] = [InstallableRef("redis", CACHE)]

    def before_copy_templates(self) -> None:
        # rendered into applications/celery.py.j2 via {{ project_name }}
        ...

    def after_pixi_install(self) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.add_service(CELERY_WORKER_DOCKER_SERVICE, [])

    def after_pixi_remove(self) -> None:
        compose = DockerComposeManager(self.structure.root)
        compose.remove_service(CELERY_WORKER_DOCKER_SERVICE, [])
```

## Templates directory

```
djdevx/providers/task_queue/celery/
├── __init__.py
└── templates/
    ├── applications/
    │   └── celery.py.j2            # → applications/celery.py (Celery app, {{ project_name }})
    ├── tasks.py                    # → tasks.py    (sample @shared_task)
    └── settings/
        └── django/
            └── celery.py           # → settings/django/celery.py
```

`settings/django/celery.py` defines a `CelerySettings(AppBaseSettings)` class.
It reads `redis_port` (populated from `REDIS_PORT` in `.env.ddx` by the cache
dev service) so the broker/result backends point at the running native Redis
cache, and overrides them to `redis://cache:6379/{0,1}` via
`get_devcontainer_overrides()` in a devcontainer.

The `applications/celery.py` template ends with a guarded otel hook so
worker/Beat processes are instrumented when the `otel` feature is installed:

```python
try:
    from otel.setup import setup_otel

    setup_otel()
except ImportError:
    pass
```

## Broker via needs

Task queues declare their broker as a `needs` entry so `ddx task-queue add
celery` auto-installs the Redis cache first. Removing the task queue leaves the
cache in place (it is a dependency of the task queue, not owned by it).

## Devcontainer worker service

Worker services are **built from the project's own image** (`build:
{context, dockerfile}`) rather than a published image: they must run the same
pixi environment as the main container, which only exists after the
devcontainer builds. See `docker_compose_manager.py::ServiceConfig` for the
`build`/`image` alternation.

## Native dev service

Register a pixi-native daemon for `ddx dev` in `services/celery.py`:
`CeleryWorkerService` (category `task-queue`) and, for schedulers,
`CeleryBeatService` (category `scheduler`). These are **portless** pid-file
daemons (no `port_env_key`, liveness = recorded pid still alive) modeled on the
OTel collector. Register them in `services/registry.py`; the category resolvers
(`resolve_task_queue_dev_service`, `resolve_scheduler_dev_service`) use
`ProjectTracking().installed(Section.TASK_QUEUE | SCHEDULER)`.

## Single-instance constraint

```
$ ddx task-queue add rq
A task-queue (celery) is already installed. Only one task queue can be installed at a time.
```

## CLI commands

```
ddx task-queue add [NAME] [-v]
ddx task-queue remove [NAME] [-v]
ddx task-queue list
```

## Testing

```bash
ddx task-queue add celery
ddx task-queue list
ddx task-queue remove celery
```

The CLI integration tests (`tests/task_queue/test_celery.py`) verify the
auto-installed broker (`needs`), the pixi dependency, the `celery.py`/`tasks.py`/
settings templates, the compose worker service, and that removal keeps the
broker cache installed. Daemon behavior is covered separately in
`tests/services/test_celery_service.py`.

## Related

- [Common Concepts](creating-an-installable.md) — shared pattern, variants, params, hooks, templates
- [Task-Queue Architecture](task-queue-architecture.md) — BaseTaskQueue details
- [Adding a Scheduler](adding-a-scheduler.md) — consumer pattern (`needs` on a task queue)
- [Installable System](installable-system.md) — Shared infrastructure
- [Deployment Architecture](deployment-architecture.md) — Docker/DevContainer setup
