# Local Development Environment

`ddx dev` hides all dev-environment complexity behind a single command group.
Postgres, Redis, and Celery (worker + Beat) run **natively** via pixi
(`initdb`/`pg_ctl`, `redis-server`, `celery`) — no Docker required. Data lives
under `.pixi/devdata/` in your project.

`ddx database add` / `ddx cache add` / `ddx task-queue add` / `ddx scheduler
add` still wire up Docker Compose for the devcontainer path; `ddx dev` is the
pixi-native local path and is independent of that wiring.

## Command Tree

```
ddx dev                              # shows help
├── start       [args...]            # bring up everything (idempotent) then run the server
├── runserver   [args...]            # just run the correct server command
├── up                               # start installed db/cache/task-queue/scheduler services
├── down                             # stop installed db/cache/task-queue/scheduler services
├── status                           # services up/down, migrate state, settings
├── database
│   ├── init                         # start postgres + migrate if pending
│   ├── reset                        # flush all data, keep service running
│   └── purge                        # stop + delete .pixi/devdata/postgres
├── cache
│   ├── init                         # start redis
│   ├── reset                        # FLUSHALL, keep service running
│   └── purge                        # stop + delete .pixi/devdata/redis
├── task-queue
│   ├── init                         # start the celery worker daemon
│   ├── reset                        # restart the worker
│   └── purge                        # stop + delete .pixi/devdata/celery/worker
├── scheduler
│   ├── init                         # start the celery beat daemon
│   ├── reset                        # restart beat
│   └── purge                        # stop + delete .pixi/devdata/celery/beat
└── otel
    ├── init                         # start the otel collector + OpenObserve
    ├── reset                        # flush telemetry data
    └── purge                        # stop + delete .pixi/devdata/otel*
```

## Getting Started

From the project root:

```bash
cd myproject
ddx dev start
```

`ddx dev start` will, in order:

1. Initialize dev configs and secrets (`settings configs init dev` +
   `settings secrets init dev`; both are skip-aware).
2. If a database is installed: start it if `pg_isready` fails, then run
   `manage.py migrate` only if `manage.py migrate --check` reports pending.
3. If a cache is installed: start redis if `redis-cli ping` fails.
4. If a task queue is installed: start the Celery worker daemon.
5. If a scheduler is installed: start the Celery Beat daemon.
6. Run the dev server in the foreground.

`pixi` is a prerequisite; check it with `ddx requirement verify`.

Flags:

| Flag | Description |
|------|-------------|
| `--skip-settings` | Skip settings configs/secrets init |
| `--skip-migrate` | Skip database migrations |
| `--verbose` / `-v` | Show full pixi output |

Any remaining arguments are forwarded to the dev server command.

## Server Command Selection

`ddx dev start` and `ddx dev runserver` share the same server-command logic.
If `django-tailwind-cli` is tracked under `[packages]` in `djdevx.toml`:

```bash
pixi run python manage.py tailwind runserver
```

otherwise:

```bash
pixi run python manage.py runserver 0.0.0.0:8000
```

Extra arguments are forwarded through to the underlying command. For example:

```bash
ddx dev runserver --port 9000
ddx dev runserver --help    # forwarded to Django's runserver --help
```

`--help` on `runserver` is forwarded to the underlying Django command instead
of showing the CLI help.

When `django-extensions` is installed, `tailwind runserver` delegates to
`runserver_plus`, which serves the app through the Werkzeug debugger. Its
access and error logs are emitted on the `werkzeug` logger with propagation
disabled, so the OTel feature captures them with a dedicated plugin — with
observability installed, requests show up in OpenObserve without any extra
configuration.

## Service Lifecycle

`ddx dev up` starts installed database/cache/task-queue/scheduler services
(idempotent) and `ddx dev down` stops them. Because only one database, one
cache, one task queue, and one scheduler can be installed at a time, these
commands always act on those single installed providers.

Per-service control is available under `ddx dev database`, `ddx dev cache`,
`ddx dev task-queue`, and `ddx dev scheduler`:

- **init** — start the service (database also migrates if pending).
- **reset** — flush all data, keep the service running
  (db: `manage.py flush --noinput`; cache: `redis-cli FLUSHALL`; worker/beat:
  restart the daemon).
- **purge** — stop (if running) and delete `.pixi/devdata/<provider>`; the
  next `init`/`start` re-initializes from scratch and picks a fresh port (the
  portless worker/Beat daemons have no port to pick).

All three commands warn and exit if the provider is not installed or has no
native service support.

## Status

`ddx dev status` shows:

- installed database/cache/task-queue/scheduler/otel and whether each service
  is up or down
- migration state (via `manage.py migrate --check`)
- the settings state via `settings secrets list dev` and
  `settings configs list dev`

When services are reported down, a diagnostic summary is printed explaining
why each failed service is unreachable (e.g. the Postgres log path when the
log file exists).

## Data Directory

All native service data lives under `.pixi/devdata/`:

```
.pixi/devdata/
├── postgres/          # initdb data directory + postgres.log
├── redis/             # redis AOF data
├── celery/
│   ├── worker/        # pid file + celery.log
│   └── beat/          # pid file + celery-beat.log
└── otel/              # collector + openobserve data
```

`.pixi/` is already gitignored by pixi, so dev data never gets committed.

Removing a provider with `ddx database remove postgres`, `ddx cache remove
redis`, `ddx task-queue remove celery`, or `ddx scheduler remove celery-beat`
also wipes its `.pixi/devdata/<provider>` directory, so no orphaned data
remains.

## Service Ports (`.env.ddx`)

Native services bind to **random OS-assigned ports** that persist across
restarts under `.pixi/devdata/<service>/port`. Whenever a service starts (or
`ddx dev runserver`/`status` refreshes), its port is also published to a
generated **`.env.ddx`** file at the project root:

```dotenv
# Generated by ddx — dev service ports. Do not edit by hand.
POSTGRES_PORT=41237
REDIS_PORT=55210
OTEL_COLLECTOR_PORT=49871
```

The settings package reads `.env.ddx` as part of its dotenv chain, so plain
`pixi run python manage.py migrate` (or `createsuperuser`, shell_plus, …)
connects to the right port with no manual env setup. The Celery broker/result
backends read `REDIS_PORT` the same way, so `pixi run celery -A applications.celery worker`
uses the running native Redis cache.

Precedence (highest wins):

1. Real environment variables (e.g. `POSTGRES_PORT=5432 pixi run ...`)
2. `.env` — your personal/CI overrides (you can pin a port here)
3. `.env.ddx` — generated; never edit by hand, it is rewritten on start
4. Settings-class dev defaults (5432 / 6379 / 4318)

`.env.ddx` is gitignored (matches the generated `.env.*` rule) and entries for
a service are removed when you `purge`/remove that provider.

## Dev Defaults

Local services use the generated settings' dev defaults:

| Service | Host:Port | User | Password |
|---------|-----------|------|----------|
| PostgreSQL | `localhost:<random>` | `postgres` | `password` |
| Redis | `localhost:<random>` | — | `redis_password` |

Ports are random per project and published in `.env.ddx` (see
[Service Ports](#serviceportsenvddx)).
The passwords fall back to `.secrets/postgres_password` /
`.secrets/redis_password` if those files exist.

Celery worker/Beat daemons are **portless** — they expose no TCP endpoint, so
liveness is tracked via their pid file under
`.pixi/devdata/celery/`. Their logs go to `.pixi/devdata/celery/worker/celery.log`
and `.pixi/devdata/celery/beat/celery-beat.log`.

## Finding More

See the [Full Manual](../cli/manual.md) for the complete command reference.
