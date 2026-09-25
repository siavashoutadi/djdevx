# Task Queue Management

`djdevx` can manage and configure task queues for development with devcontainer
support. **Only one task queue can be installed at a time.**

Currently only Celery is supported, but more task queues will be added in the
future.

`ddx task-queue add celery` auto-installs the **Redis cache** as the Celery
broker (`needs`), so producer/worker and scheduled tasks have a backend to
talk to.

## Usage

```bash
# Install a task queue (auto-installs the Redis cache broker)
ddx task-queue add celery

# Remove a task queue
ddx task-queue remove celery

# List all task queues with install status
ddx task-queue list

# Interactive selection (omit [NAME])
ddx task-queue add
ddx task-queue remove
```

## Shell Autocompletion

The `[NAME]` argument supports tab completion:
- `ddx task-queue add <TAB>` — lists available (not installed) task queues
- `ddx task-queue remove <TAB>` — lists installed task queues

## Single-Instance Constraint

Only one task queue can be installed at a time. If one is already installed,
attempting to add another will show an error:

```
$ ddx task-queue add rq
A task-queue (celery) is already installed.
Only one task queue can be installed at a time.
```

Remove the existing task queue first, then install the new one.

## What gets installed

`ddx task-queue add celery`:

- Adds `celery` (pypi) to the pixi environment.
- Auto-installs the Redis cache as the broker (if not already installed).
- Generates the Celery app (`applications/celery.py`), a sample `tasks.py`, and
  `settings/django/celery.py` (`CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` —
  dev defaults point at the local Redis cache on `REDIS_PORT` and embed the
  `redis_password` (matching the running Redis dev service); in a devcontainer
  they point at the password-protected `cache` compose service).
- Wires a `celery-worker` docker-compose service for the devcontainer path
  (builds the same image, runs `pixi run celery -A applications.celery worker`).

Settings load the redis password from the same sources as the cache
(`REDIS_PASSWORD` env, `.env`, or `.secrets/redis_password`), so the broker and
result backend authenticate against the cache exactly like `CACHES` does.

The app lives in the `applications` package — not as a root-level `celery.py` —
so the `celery` module name stays free for the installed `celery` package; a
root `celery.py` would shadow it and break both `celery -A ...` resolution and
the opentelemetry celery instrumentation (`import celery`).

Task modules are auto-discovered with `app.autodiscover_tasks()`, so define
`@shared_task` functions in any Django app's `tasks.py`.

## Pixi-Native Local Dev

For day-to-day local development, `ddx dev` runs the Celery worker **natively**
as a pixi background daemon — no Docker:

```bash
ddx dev up              # start redis + the celery worker
ddx dev task-queue init # start the celery worker
ddx dev task-queue reset # restart the worker
ddx dev task-queue purge # stop + delete .pixi/devdata/celery/worker
```

Daemon logs live in `.pixi/devdata/celery/worker/celery.log`. See
[Local Development](dev.md) for details.

## Observability

With the `otel` feature installed, workers are instrumented automatically:
`opentelemetry-instrumentation-celery` is installed as a peer and the generated
`applications/celery.py` calls `setup_otel()` so task spans appear in OpenObserve.

## Finding More

See the [Full Manual](../cli/manual.md) for complete reference.
