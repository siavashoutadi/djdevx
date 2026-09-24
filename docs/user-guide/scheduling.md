# Scheduling

`djdevx` can manage schedulers (time-based periodic task triggers) for
development with devcontainer support. **Only one scheduler can be installed
at a time.**

Currently only Celery Beat is supported, but more schedulers will be added in
the future.

`ddx scheduler add celery-beat` auto-installs the **Celery task queue** (`needs`),
which in turn installs the Redis cache broker.

## Usage

```bash
# Install a scheduler (auto-installs the Celery task queue)
ddx scheduler add celery-beat

# Remove a scheduler
ddx scheduler remove celery-beat

# List all schedulers with install status
ddx scheduler list

# Interactive selection (omit [NAME])
ddx scheduler add
ddx scheduler remove
```

## Shell Autocompletion

The `[NAME]` argument supports tab completion:
- `ddx scheduler add <TAB>` — lists available (not installed) schedulers
- `ddx scheduler remove <TAB>` — lists installed schedulers

## Single-Instance Constraint

Only one scheduler can be installed at a time. If one is already installed,
attempting to add another will show an error:

```
$ ddx scheduler add rq-scheduler
A scheduler (celery-beat) is already installed.
Only one scheduler can be installed at a time.
```

Remove the existing scheduler first, then install the new one.

## What gets installed

`ddx scheduler add celery-beat`:

- Adds `django-celery-beat` (pypi) to the pixi environment.
- Auto-installs the Celery task queue (if not already installed).
- Adds `django_celery_beat` to `INSTALLED_APPS` (`settings/apps/celery.py`).
- Switches to the database-backed scheduler with
  `CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"`
  (`settings/django/celery_beat.py`).
- Wires a `celery-beat` docker-compose service for the devcontainer path
  (builds the same image, runs `pixi run celery -A applications.celery beat`).

Because the scheduler is database-backed, apply migrations after install so the
`django_celery_beat` tables exist:

```bash
ddx dev start   # runs migrate automatically
```

## Pixi-Native Local Dev

For day-to-day local development, `ddx dev` runs Celery Beat **natively** as a
pixi background daemon — no Docker:

```bash
ddx dev up            # start redis + worker + beat
ddx dev scheduler init # start celery beat
ddx dev scheduler reset # restart beat
ddx dev scheduler purge # stop + delete .pixi/devdata/celery/beat
```

Daemon logs live in `.pixi/devdata/celery/beat/celery-beat.log`. See
[Local Development](dev.md) for details.

## Finding More

See the [Full Manual](../cli/manual.md) for complete reference.
