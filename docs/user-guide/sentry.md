# Sentry

`ddx features add sentry` wires [Sentry](https://sentry.io) error monitoring,
performance tracing, and log shipping into a generated project. It installs the
modern `sentry-sdk` (not the deprecated `sentry-django`), scaffolds a `sentry`
Django app, and initializes the SDK for every process: web server, Celery
workers, Celery Beat, and management commands.

## Usage

```bash
# Install the feature
ddx features add sentry

# Remove it again
ddx features remove sentry

# List features with install status
ddx features list
```

## After installing: set the DSN

The DSN (Data Source Name) identifies your Sentry project. The feature treats it
as a **required secret with no default**, so it never writes a placeholder that
would silently drop every event.

That also means **Django cannot start until the DSN is set.** Grab it from
Sentry → your project → Settings → Client Keys, then run:

```bash
# Local development
ddx settings secrets init dev

# Production (run from the deployment target)
ddx settings secrets init prod
```

The DSN is written to `.secrets/sentry_dsn` (dev) and is picked up automatically
by deployment generation as a Docker secret or Kubernetes secret. See
[Managing Settings](managing-settings.md).

Until you do, any Django command fails with a clear pydantic error:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for SentrySettings
sentry_dsn
  Field required [type=missing, ...]
```

## Verifying it works

With `DEBUG` on, a verification endpoint is mounted at `/sentry-debug/`:

```bash
# In development only
curl http://localhost:8000/sentry-debug/
```

The request intentionally raises a `ZeroDivisionError`. If the request 500s and
the event shows up in Sentry within a few seconds, the SDK is wired correctly.
With `DEBUG` off the route is not mounted at all and 404s like any other unknown
path — delete `sentry/urls.py` and `urls/apps/sentry.py` once you have verified
the pipeline and no longer want the endpoint.

## What gets installed

`ddx features add sentry` adds:

- `sentry-sdk` (pypi) to the pixi environment.
- A `sentry` app at the project root:
  - `sentry/apps.py` — `SentryConfig.ready()` calls `setup_sentry()`. `ready()`
    is the right hook because it runs exactly once per process, and Django's app
    registry is populated before Celery workers execute any task, so the SDK is
    initialized on worker startup as Sentry requires.
  - `sentry/setup.py` — maps the `SENTRY_*` settings onto
    `sentry_sdk.init()`. Idempotent (guarded per process) and never raises:
    broken monitoring can never take the app registry down.
  - `sentry/views.py`, `sentry/urls.py` — the `/sentry-debug/` endpoint.
- `settings/apps/sentry.py` — the `SentrySettings` config surface, plus
  `INSTALLED_APPS += ["sentry"]`.
- `urls/apps/sentry.py` — mounts the endpoint, DEBUG-gated.

The package is named `sentry` but shadows nothing: the SDK's import name is
`sentry_sdk`.

## Configuration

Every option is a pydantic-settings field in `settings/apps/sentry.py`, so it
can be set per environment (`.env`, `/run/configs/app-config`, or the
environment itself). Field names deliberately mirror Sentry's own variables —
`sentry_dsn` → `SENTRY_DSN`, `sentry_environment` → `SENTRY_ENVIRONMENT`,
`sentry_release` → `SENTRY_RELEASE`, `sentry_debug` → `SENTRY_DEBUG` — so
container and cluster deployments can use either convention.

| Setting | Default | Purpose |
|---------|---------|---------|
| `sentry_dsn` | *required* | DSN. A secret, not a config var. |
| `sentry_environment` | `""` in prod, `development` in dev | Sentry environment. Empty falls back to the SDK default (`production`). |
| `sentry_release` | `""` | Release identifier (e.g. a git SHA). Empty falls back to the SDK default. |
| `sentry_sample_rate` | `1.0` | Fraction of error events to send. |
| `sentry_traces_sample_rate` | `0.0` in prod, `1.0` in dev | Fraction of transactions to trace. `0.0` disables performance monitoring. |
| `sentry_profiles_sample_rate` | `0.0` | Fraction of traces to profile. Profiling is a paid add-on; keep at `0.0` unless you use it. |
| `sentry_profile_lifecycle` | `trace` | `trace` or `manual`. |
| `sentry_send_default_pii` | `False` | Send user IPs, usernames, and request bodies. Off by default — turning it on is a privacy decision, not a default. |
| `sentry_max_breadcrumbs` | `100` | Breadcrumbs kept per event. |
| `sentry_max_request_body_size` | `medium` | `never`, `small`, `medium`, or `always`. |
| `sentry_attach_stacktrace` | `False` | Attach stack traces to messages as well as exceptions. |
| `sentry_include_local_variables` | `True` | Include local variables on captured exceptions. |
| `sentry_middleware_spans` | `False` | Trace individual middleware. Off by default — it is high-volume and rarely worth the cost. |
| `sentry_cache_spans` | `False` | Trace cache reads/writes. |
| `sentry_signals_spans` | `True` | Trace Django signals. |
| `sentry_http_methods_to_capture` | common methods | HTTP methods that get request breadcrumbs. |
| `sentry_capture_logs` | `False` in prod, `True` in dev | Ship structured logs. |
| `sentry_logs_level` | `INFO` (20) | Minimum level for log events. |
| `sentry_breadcrumb_level` | `INFO` (20) | Minimum level for log breadcrumbs. |
| `sentry_event_level` | `ERROR` (40) | Log level that becomes a Sentry event. |
| `sentry_debug` | `False` | Verbose SDK logging. Mirrors `SENTRY_DEBUG`. |

The three sampling knobs are the ones you will actually tune per environment:

```bash
# .env for local development
SENTRY_TRACES_SAMPLE_RATE=1.0
```

For production, set the rates explicitly rather than relying on the defaults —
tracing is off until you opt in:

```bash
# prod ConfigMap / deployment environment
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=$(git rev-parse --short HEAD)
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.0
```

`ddx settings configs init prod` only prompts for variables that have no class
default, so the table above stays quiet in production.

## Celery and Celery Beat

Sentry's Celery integration is bundled inside `sentry-sdk`; no extra package is
needed. It is enabled automatically when Celery is installed.

| Setting | Default | Purpose |
|---------|---------|---------|
| `sentry_celery_propagate_traces` | `True` | Propagate the parent trace into tasks, so a request and the tasks it triggers appear in one trace. |
| `sentry_celery_exclude_beat_tasks` | `[]` | Beat task names to exclude from check-ins. |
| `sentry_celery_monitor_beat_tasks` | `True` (Beat only) | Report periodic-task check-ins to **Sentry Crons**, so a missed or slow schedule is visible instead of silently disappearing. |

These live in `settings/apps/sentry_celery.py` and
`settings/apps/sentry_celery_beat.py`, which djdevx copies in and out
automatically alongside `ddx task-queue add celery` /
`ddx scheduler add celery-beat`. You can also add or remove the task queue and
scheduler at any time afterwards — the matching settings file follows.

`propagate_traces` needs trace continuity to be useful, so leave
`sentry_traces_sample_rate` above `0.0` in any environment where you expect to
see task spans.

## Removing

```bash
ddx features remove sentry
```

This removes the `sentry` app, `settings/apps/sentry.py`, `urls/apps/sentry.py`,
the Celery peer settings, the `sentry-sdk` dependency, and the tracking entry.

Your DSN is **kept** in `.secrets/sentry_dsn`. It was entered by hand rather
than generated by the feature, so removing it would destroy a value you would
need again on reinstall. Delete the file yourself if you want it gone.

## Troubleshooting

**No events arrive, and the request still 500s.** The view raises the error
before the SDK can flush. Check Sentry's status page, then confirm the DSN is
readable: `pixi run python -c "import django,os;os.environ.setdefault('DJANGO_SETTINGS_MODULE','settings');django.setup();from django.conf import settings;print(settings.SENTRY_DSN[:20])"`.

**Nothing at all happens — no error, no event.** The DSN is probably empty. An
empty DSN makes `setup_sentry()` return early and the SDK stays disabled
intentionally; `manage.py` would have failed earlier if the secret were missing
entirely.

**Events are missing request data.** `sentry_send_default_pii` is `False` and
`sentry_max_request_body_size` is `medium`, so IPs, users, and large bodies are
withheld. Raise them deliberately.

**No traces in production.** `sentry_traces_sample_rate` defaults to `0.0` in
prod — performance monitoring is off until you opt in. Set it above `0.0`.

**`DidNotEnable` or Celery warnings at startup.** The Celery integration could
not be enabled (usually Celery missing). `sentry/setup.py` logs a warning and
continues; task errors are still reported, but task traces and check-ins are
not.

**Celery task errors are missing entirely.** Check that
`settings/apps/sentry_celery.py` exists. Without it, the Celery integration is
never registered.

## Finding More

- [Sentry Python SDK options](https://docs.sentry.io/platforms/python/configuration/options/)
- [Sentry Django integration](https://docs.sentry.io/platforms/python/integrations/django/)
- [Sentry Celery integration](https://docs.sentry.io/platforms/python/integrations/celery/)
- [Managing Settings](managing-settings.md) for secrets and config vars
- [Task Queues](task-queues.md) / [Scheduling](scheduling.md)
