# Local Development Environment

`ddx dev` hides all dev-environment complexity behind a single command group.
Postgres and Redis run **natively** via pixi conda packages
(`initdb`/`pg_ctl`, `redis-server`) — no Docker required. Data lives under
`.pixi/devdata/` in your project.

`ddx database add` / `ddx cache add` still wire up Docker Compose for the
devcontainer path; `ddx dev` is the pixi-native local path and is independent
of that wiring.

## Command Tree

```
ddx dev                              # shows help
├── start       [args...]            # bring up everything (idempotent) then run the server
├── runserver   [args...]            # just run the correct server command
├── up                               # start installed db/cache services
├── down                             # stop installed db/cache services
├── status                           # services up/down, migrate state, settings
├── database
│   ├── init                         # start postgres + migrate if pending
│   ├── reset                        # flush all data, keep service running
│   └── purge                        # stop + delete .pixi/devdata/postgres
└── cache
    ├── init                         # start redis
    ├── reset                        # FLUSHALL, keep service running
    └── purge                        # stop + delete .pixi/devdata/redis
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
4. Run the dev server in the foreground.

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

## Service Lifecycle

`ddx dev up` starts installed database/cache services (idempotent) and
`ddx dev down` stops them. Because only one database and one cache can be
installed at a time, these commands always act on that single installed
provider.

Per-service control is available under `ddx dev database` and
`ddx dev cache`:

- **init** — start the service (database also migrates if pending).
- **reset** — flush all data, keep the service running
  (db: `manage.py flush --noinput`; cache: `redis-cli FLUSHALL`).
- **purge** — stop (if running) and delete `.pixi/devdata/<provider>`; the
  next `init`/`start` re-initializes from scratch and picks a fresh port.

All three commands warn and exit if the provider is not installed or has no
native service support.

## Status

`ddx dev status` shows:

- installed database/cache and whether each service is up or down
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
└── redis/             # redis AOF data
```

`.pixi/` is already gitignored by pixi, so dev data never gets committed.

Removing a provider with `ddx database remove postgres` or
`ddx cache remove redis` also wipes its `.pixi/devdata/<provider>` directory,
so no orphaned data remains.

## Dev Defaults

Local services use the generated settings' dev defaults:

| Service | Host:Port | User | Password |
|---------|-----------|------|----------|
| PostgreSQL | `localhost:5432` | `postgres` | `password` |
| Redis | `localhost:6379` | — | `redis_password` |

The passwords fall back to `.secrets/postgres_password` /
`.secrets/redis_password` if those files exist.

## Finding More

See the [Full Manual](../cli/manual.md) for the complete command reference.
