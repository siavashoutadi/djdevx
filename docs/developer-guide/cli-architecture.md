# CLI Overview

`djdevx` uses [Typer](https://typer.tiangolo.com/) for its CLI. Commands are
organized as nested sub-apps with `no_args_is_help=True` on all levels.

## Entry Points

- `djdevx` — full command name
- `ddx` — shorthand alias

Both point to `djdevx.main:app`.

## Command Tree

```
ddx
├── version                                      # Show version
├── requirement
│   ├── verify                                      # Check system requirements
│   └── install [-t TOOL] [--dry-run] [-v]          # Install required tools
├── new                                          # Create new Django project
│     [--project-name] [--project-description]
│     [--project-directory] [--python-version]
│     [--git-init / --no-git-init] [-v]
├── packages
│   ├── add [NAME ...] [-p provider] [-v]        # Install packages (multi)
│   ├── remove [NAME ...] [-p provider] [-v]     # Remove packages (multi)
│   └── list                                     # List packages (check/cross table)
├── frameworks
│   ├── add [NAME ...] [-v]                      # Add CSS/JS frameworks (multi)
│   ├── remove [NAME ...] [-v]                   # Remove frameworks (multi)
│   └── list                                     # List frameworks
├── features
│   ├── add [NAME] [-p provider] [-v]            # Install a feature
│   ├── remove [NAME] [-p provider] [-v]         # Remove a feature
│   └── list                                     # List features
├── create app                                   # Scaffold new Django app
├── database
│   ├── add [NAME] [-v]                          # Add a database (single only)
│   ├── remove [NAME] [-v]                       # Remove a database
│   └── list                                     # List databases
├── cache
│   ├── add [NAME] [-v]                          # Add a cache (single only)
│   ├── remove [NAME] [-v]                       # Remove a cache
│   └── list                                     # List caches
├── settings
│   ├── secrets {init,list,verify} [ENV]
│   └── configs {init,list,verify} [ENV]
├── dev
│   ├── start [args...] [--skip-settings] [--skip-migrate] [-v]
│   ├── runserver [args...]                  # tailwind-aware; args forwarded
│   ├── up                                   # start installed dev services
│   ├── down                                 # stop installed dev services
│   ├── status                               # services up/down, migrations, settings
│   ├── credentials                          # endpoints + credentials table
│   ├── database {init,reset,purge}          # pixi-native postgres
│   ├── cache {init,reset,purge}             # pixi-native redis
│   └── otel {init,reset,purge}              # pixi-native otel collector + OpenObserve
└── deployment
    └── docker-compose {generate,verify}
```

## CLI Conventions

- **`no_args_is_help=True`** — Every `typer.Typer()` instance uses this so
  running a command without arguments shows its help.

- **Generic domain factory** — The five installable categories
  (`packages`, `features`, `frameworks`, `database`, `cache`) no longer hand-
  write `add`/`remove`/`list` modules. Each category's `__init__.py` is a
  three-line declaration built by `djdevx/cli/factory.py::domain_app()`:

  ```python
  # djdevx/providers/packages/__init__.py
  from ..cli.factory import domain_app
  from ._base import BasePackage
  from ._registry import PACKAGE_REGISTRY

  app = domain_app(
      BasePackage,
      label="Package",
      registry=PACKAGE_REGISTRY,
      discover_path=__path__,
      discover_name=__name__,
      supports_provider=True,   # expose -p/--provider variant selection
      supports_multi=True,      # batch add/remove of multiple names
  )
  ```

  `domain_app()` generates the `add`/`remove`/`list` commands, NAME
  autocompletion (installed vs available), interactive fallback prompts, the
  shared Rich check/cross list table, and per-category behaviors via flags:
  `single=True` for database/cache, `supports_multi` for packages/features/
  frameworks.

- **Positional Arguments with Autocompletion** — The generated `[NAME]`
  argument uses `typer.Argument(autocompletion=...)`; completions come from
  `autocomplete_installable()` in `installable/ops/tracking.py`.

- **Interactive fallback** — If `[NAME]` is omitted, the generated command
  prompts interactively using questionary checkboxes or selects
  (`orchestrator.select_installable` / `select_installed`).

- **Discovery via discover_and_register** — `domain_app()` calls
  `core/discovery.discover_and_register()` on the category's package path,
  importing every payload module so its `@register` decorator runs before the
  commands execute.

- **Folder-per-category payloads** — Concrete providers live under
  `djdevx/providers/<domain>/`:

  ```
  providers/features/
  ├── __init__.py        # 3-line domain_app declaration
  ├── _base.py           # BaseFeature(Provider) — thin kind pin
  ├── _registry.py       # FEATURE_REGISTRY + @register
  ├── otel/
  │   └── __init__.py    # @register OtelFeature(BaseFeature) + templates/
  └── pwa/
      └── __init__.py
  ```

- **Validation via callbacks** — Input validation uses `callback=func` on
  `typer.Option()`. The callback raises `typer.BadParameter(...)` on invalid
  input and returns the (possibly transformed) valid value.

- **Error exits** — Commands abort with `typer.Exit(code=1)` on failures
  (missing dependencies, invalid state). Early success exits use
  `typer.Exit(0)` (e.g., empty list results).

- **Argument passthrough** — `ddx dev start` and `ddx dev runserver` forward
  unknown arguments to the underlying Django command using
  `context_settings={"ignore_unknown_options": True, "allow_extra_args": True}`
  plus a `typer.Context` parameter read via `ctx.args`. Flags on the outer
  command must come before forwarded arguments. `runserver` additionally
  disables its own `--help` option so `ddx dev runserver --help` is forwarded
  to the Django command.

## Dev Command Group

`ddx dev` is split into thin command modules under `djdevx/dev/` (`start.py`,
`runserver.py`, `up.py`, `down.py`, `status.py`, `credentials.py`,
`database.py`, `cache.py`, `otel.py`). Shared behavior lives in:

- **`djdevx/cli/dev.py`** — the declarative `ddx dev start` pipeline
  (`run_start`): settings init → database up → migrate → cache up → render
  endpoints → dev server. Each native service is started exactly once; in a
  devcontainer the compose stack owns the services and only
  settings/migrations/server run. `dev/start.py` is a thin CLI wrapper that
  delegates here.
- **`services/registry.py`** — the service registry (`SERVICE_REGISTRY`) with
  category-filtered resolvers: `resolve_database_dev_service()`,
  `resolve_cache_dev_service()`, `resolve_otel_dev_services()`,
  `resolve_openobserve_dev_service()`, `resolve_dev_services()`. Each reads
  `djdevx.toml` tracking to find the installed provider(s) and instantiate the
  matching `BaseDevService`. Because only one database and one cache can be
  installed at a time, `ddx dev` commands always act on those.
- **`dev/context.py` + `dev/render.py`** — build the service endpoint snapshot
  (native or devcontainer) and render the shared services/credentials tables.
- **`utils/django/manage_commands.py`** — `ManageCommands` wraps Django
  `manage.py` commands (e.g. `migrations_pending()`) over the `PixiRunner`
  (`core/process.py`), shared by `start`, `status`, and `database`.
- **`dev/runserver.py`** — `server_command()` resolves the tailwind-aware dev
  server command, shared by `runserver` and `start`.

## Installable Category Pattern

All five installable categories follow the same architectural pattern.
See [Installable System](installable-system.md) for the full reference. The
entire category CLI is the `domain_app()` declaration shown above.

## Adding a New Category

To add a new installable category (e.g., "monitoring"):

1. Create `djdevx/providers/monitoring/` with the standard scaffolding:
   ```
   providers/monitoring/
   ├── __init__.py        # 3-line domain_app(...) declaration
   ├── _base.py           # BaseMonitoring(Provider) with kind = MONITORING_KIND
   ├── _registry.py       # MONITORING_REGISTRY + @register
   └── <name>/            # payload modules, each with templates/
   ```

2. Add a `Section` enum member (`utils/tracking/sections.py`) and a kind
   constant in `djdevx/provider.py` mapping it.

3. Track installs via `ProjectTracking` in `djdevx.toml`:
   ```python
   project = ProjectTracking()
   project.is_installed(Section.MONITORING, "prometheus")
   project.add(Section.MONITORING, "prometheus", "Prometheus")
   ```

4. Register in `djdevx/main.py`:
   ```python
   from .providers.monitoring import app as monitoring_app
   app.add_typer(monitoring_app, name="monitoring", help="Manage monitoring tools")
   ```

## References

- [Installable System](installable-system.md) — Full architecture reference
- [Creating an Installable](creating-an-installable.md) — Common concepts and how-to guides with examples
- [CLI Full Manual](../cli/manual.md) — Auto-generated command reference
