# Task-Queue Architecture

Task queues manage async-work providers (Celery) with Docker Compose
integration and `needs`-based broker setup. Only **one** task queue can be
installed at a time — same constraint as databases and caches.

## BaseTaskQueue

`BaseTaskQueue` (`djdevx/providers/task_queue/_base.py`) is a thin subclass of
the shared `Provider` base pinned to `TASK_QUEUE_KIND`. It adds no additional
attributes — all behavior comes from `Provider` / `Installable`.

### Single-Instance Constraint

The `task-queue` `InstallableKind` has `single_installable=True`, enforced by
the `domain_app(..., single=True)` CLI (same message pattern as database/cache).

## Section & Kind Wiring

A task queue spans the whole stack — add it in four places:

1. `utils/tracking/sections.py` — `Section.TASK_QUEUE = "task-queue"`
2. `installable/models.py` — `TASK_QUEUE = InstallableKind("task-queue", Section.TASK_QUEUE)` + `KIND_BY_SECTION`
3. `provider.py` — `TASK_QUEUE_KIND = InstallableKind(..., Section.TASK_QUEUE)` (the domain's kind constant)
4. `main.py` — `app.add_typer(task_queue_app, name="task-queue", help=...)`

`providers/task_queue/_registry.py` exposes `TASK_QUEUE_REGISTRY`, `register`,
`get_task_queue`, `list_task_queues`; `__init__.py` is a
`domain_app(..., single=True)` declaration.

## Broker via `needs`

The Celery provider declares `needs=[InstallableRef("redis", CACHE)]`, so
installing a task queue auto-installs its broker cache. The broker is a
dependency, not owned — removing the task queue leaves the cache installed.

## Devcontainer Worker Service

Workers are built from the project's own image:

```python
CELERY_WORKER_DOCKER_SERVICE: ServiceConfig = {
    "name": "celery-worker",
    "build": {"context": ".", "dockerfile": "Dockerfile"},
    "volumes": ["../:/home/devuser/workspace:cached"],
    "environment": {"DEVCONTAINER": "true"},
    "networks": ["devcontainer"],
    "depends_on": ["cache", "devcontainer"],
    "command": "/home/devuser/.pixi/bin/pixi run celery -A applications.celery worker --loglevel=info",
}
```

This requires `docker_compose_manager.py::ServiceConfig` to accept
`build: NotRequired[dict[str, str]]` alongside `image`.

## Native Dev Service

`services/celery.py::CeleryWorkerService` is a **portless pid-file daemon**
(category `task-queue`, no `port_env_key`): liveness is the recorded pid still
running (`is_pid_alive`), the log lives at
`.pixi/devdata/celery/worker/celery.log`, and it launches
`pixi run celery -A applications.celery worker --loglevel=info` in the background. It is
registered in `services/registry.py` and resolved via
`resolve_task_queue_dev_service()`.

`ddx dev start` (the declarative pipeline in `cli/dev.py`) orders services
**database → otel → migrate → cache → worker → beat** so the broker is up
before the worker connects. `dev/context.py` renders portless entries with
`port=0`; `dev/task_queue.py` exposes `init`/`reset`/`purge` under
`ddx dev task-queue`.

## Instrumentation

The generated `applications/celery.py` calls `setup_otel()` (guarded by
`ImportError`) so worker and Beat processes are instrumented when the `otel`
feature is installed. The otel feature declares the peer
`InstallableRef("celery", TASK_QUEUE)` → `opentelemetry-instrumentation-celery`
and ships `peer_templates/celery/otel/plugins/celery.py` (disabled via
`OTEL_CELERY_ENABLED=False`).

The app module deliberately lives in the `applications` package rather than at
the project root: a root-level `celery.py` would shadow the installed `celery`
package for any `import celery`, breaking `-A` resolution (workers fall back to
a default app on `amqp://localhost:5672`) and the otel celery instrumentation
(`opentelemetry-instrumentation-celery` does `from celery import signals`).

## Related

- [Installable System](installable-system.md) — Shared infrastructure
- [Add a Task Queue](adding-a-task-queue.md) — Step-by-step guide
- [Adding a Scheduler](adding-a-scheduler.md) — consumer of a task queue
- [Deployment Architecture](deployment-architecture.md) — Docker/DevContainer setup
