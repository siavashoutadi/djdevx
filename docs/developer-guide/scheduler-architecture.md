# Scheduler Architecture

Schedulers trigger time-based work on a task queue (Celery Beat) with Docker
Compose integration. Only **one** scheduler can be installed at a time — same
constraint as databases, caches, and task queues.

## BaseScheduler

`BaseScheduler` (`djdevx/providers/scheduler/_base.py`) is a thin subclass of
the shared `Provider` base pinned to `SCHEDULER_KIND`. It adds no additional
attributes — all behavior comes from `Provider` / `Installable`.

### Single-Instance Constraint

The `scheduler` `InstallableKind` has `single_installable=True`, enforced by
the `domain_app(..., single=True)` CLI.

## Section & Kind Wiring

A scheduler spans the whole stack — add it in four places:

1. `utils/tracking/sections.py` — `Section.SCHEDULER = "scheduler"`
2. `installable/models.py` — `SCHEDULER = InstallableKind("scheduler", Section.SCHEDULER)` + `KIND_BY_SECTION`
3. `provider.py` — `SCHEDULER_KIND` (the domain's kind constant)
4. `main.py` — `app.add_typer(scheduler_app, name="scheduler", help=...)`

`providers/scheduler/_registry.py` exposes `SCHEDULER_REGISTRY`, `register`,
`get_scheduler`, `list_schedulers`; `__init__.py` is a
`domain_app(..., single=True)` declaration.

## Dependency on a Task Queue

The Celery Beat provider declares `needs=[InstallableRef("celery", TASK_QUEUE)]`
(then that chain installs the Redis broker). Removing the scheduler leaves the
task queue and its broker cache in place.

## Database-Backed Storage

Celery Beat periods live in the Django database. Install writes:

- `settings/apps/celery.py` — `INSTALLED_APPS += ["django_celery_beat"]`
- `settings/django/celery_beat.py` —
  `CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"`

`manage.py migrate` creates the tables (`ddx dev start` runs it automatically).

## Devcontainer Beat Service

```python
CELERY_BEAT_DOCKER_SERVICE: ServiceConfig = {
    "name": "celery-beat",
    "build": {"context": ".", "dockerfile": "Dockerfile"},
    "volumes": ["../:/home/devuser/workspace:cached"],
    "environment": {"DEVCONTAINER": "true"},
    "networks": ["devcontainer"],
    "depends_on": ["cache", "celery-worker", "devcontainer"],
    "command": "/home/devuser/.pixi/bin/pixi run celery -A applications.celery beat --loglevel=info",
}
```

## Native Dev Service

`services/celery.py::CeleryBeatService` is a **portless pid-file daemon**
(category `scheduler`) sharing the base with the worker. It is resolved via
`resolve_scheduler_dev_service()`; `ddx dev start` starts it **after** the
worker; `dev/scheduler.py` exposes `init`/`reset`/`purge` under
`ddx dev scheduler`.

## Related

- [Installable System](installable-system.md) — Shared infrastructure
- [Add a Scheduler](adding-a-scheduler.md) — Step-by-step guide
- [Task-Queue Architecture](task-queue-architecture.md) — the producer it schedules
- [Deployment Architecture](deployment-architecture.md) — Docker/DevContainer setup
