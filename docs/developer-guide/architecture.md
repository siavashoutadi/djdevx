# Architecture

`djdevx` is a CLI tool built with [Typer](https://typer.tiangolo.com/) that
generates and manages Django projects. It uses Jinja2 templates for code
generation and pydantic-settings for configuration management.

## High-Level Design

```
CLI (Typer) ──► Orchestrator ──► Provider (Installable) ──┬── ops/pixi (install deps)
                     ▲                     │              ├── ops/scaffold (copy templates)
                     │                     │              ├── ops/secrets (generate secrets)
                     │                     │              └── ops/tracking (write djdevx.toml)
              cli/factory                  │
                     ▲                  Registry ──► Concrete provider modules
       thin domain apps ──► Auto-discovery (core/discovery)   (providers/<domain>/*)
```

The flow is: a CLI command is dispatched to the orchestrator, which resolves
dependencies, collects interactive parameters, and calls `Installable.add()`.
The provider delegates to `PixiOps` (dependency installation), `Scaffold`
(Jinja2 template rendering), `SecretsOps` (secret file generation), and
`TrackingOps` (state persistence in `djdevx.toml`). Concrete providers
(packages, features, frameworks, databases, caches) are auto-discovered via
`pkgutil.iter_modules` and registered into typed registries at startup.

## Package Layout

```
djdevx/
  core/            # shared kernel (thin, no business rules)
    process.py     # PixiRunner + pid-file / port-wait / retry helpers
    paths.py       # ProjectStructure — project-root discovery
    secrets.py     # SecretManager — .secrets/ files (0600 / dir 0700)
    console.py     # PrintConsole / NestedStep / Rich table helpers
    discovery.py   # discover_and_register() — module auto-import
  installable/     # installable-domain kernel
    models.py      # InstallableConfig, InstallParam, Variant, InstallableKind, InstallableRef
    lifecycle.py   # Installable — pydantic base with add/remove + hooks
    registry.py    # Registry[T], REGISTRIES, all_registries()
    resolver.py    # InstallableRef -> class resolution
    orchestrator.py# add_installable() / remove_installable() / selection prompts
    peers.py       # peer integration engine (sync_on_add/remove, _safe_hook)
    list_table.py  # shared Rich table for `list` commands
    ops/           # lifecycle operations used by Installable
      pixi.py      #   PixiOps — pixi add/remove
      scaffold.py  #   copy_templates / cleanup_files / restore_original_templates
      secrets.py   #   SecretsOps
      tracking.py  #   TrackingOps + section queries
      format.py    #   prek-based file formatting for generated output
  provider.py      # single Provider base + PACKAGE/FEATURE/... kind constants
  providers/       # concrete provider payloads (moved from the five domain dirs)
    packages/  features/  frameworks/  database/  cache/
      _base.py     # thin per-domain base (e.g. BasePackage(Provider)) — payload-facing
      _registry.py # per-domain Registry instance + @register decorator
      <name>/      # one package per provider, with its templates/ payload
  services/        # pixi-native local dev services (postgres, redis, otel...)
    base.py        # BaseDevService ABC (wait_until_ready, step_group, _log_debug)
    registry.py    # SERVICE_REGISTRY, register_service, category resolvers
    postgres.py redis.py otel.py binary.py
  cli/             # CLI glue
    factory.py     # generic domain_app() typer group factory (add/remove/list)
    dev.py         # declarative `ddx dev start` pipeline
  dev/  new/  create/  settings/  deployment/  database... (CLI command groups)
  main.py          # assembles the root typer app
```

## Type Hierarchy

```
InstallableConfig (pydantic BaseModel)    ← installable/models.py
  ├── install_params, pixi_packages, peer_pixi_packages, needs, secret_generators...
  └── Variant                              ← extends InstallableConfig (adds required=True)
        └── Installable                    ← installable/lifecycle.py (adds lifecycle hooks)
              └── Provider                 ← provider.py (kind parameterized; shared payload behaviour)
                    ├── BasePackage        ← providers/packages/_base.py
                    ├── BaseFeature        ← providers/features/_base.py
                    ├── BaseFramework      ← providers/frameworks/_base.py
                    ├── BaseDatabase       ← providers/database/_base.py
                    └── BaseCache          ← providers/cache/_base.py
```

Each domain's `_base.py` is a three-line subclass pinning the provider `kind`;
payload modules (`django_cors_headers`, `redis`, ...) keep importing them via
`from .._base import ...` and register through `from .._registry import
register`.

### Shared Data Types

Shared data types that span multiple modules live in `utils/types/`:

| File | Contents |
|------|----------|
| `utils/types/pixi_types.py` | `PixiPackageSpec` — conda/pypi dependency spec |

Installable-specific types live in `installable/models.py` — tightly coupled
to that subsystem (`InstallableRef`, `Variant`, `InstallableKind`, ...).

## Lifecycle

### Install Lifecycle

```
add_installable(cls, name, provider=None):
  1. _auto_install_needs(needs)         ← recursively install unmet dependencies
  2. (variant selection)                ← exclusive: pick one, additive: pick optional, simple: skip
  3. Installable.add(variant_name):
     a. before_pixi_install()           ← hook
     b. PixiOps(root).add_packages()    ← pixi add
     c. after_pixi_install()            ← hook (e.g. Docker Compose)
     d. before_copy_templates()         ← hook
     e. ops.scaffold.copy_templates()   ← Jinja2 render + copy
     f. after_copy_templates()          ← hook (e.g. CSS download, icon generation)
     g. SecretsOps(root).generate()     ← auto-generate secret files
     h. TrackingOps(section).track()    ← write djdevx.toml
```

### Remove Lifecycle

```
remove_installable(cls, name, provider=None):
  1. Installable.remove(variant_name):
     a. before_pixi_remove()            ← hook (e.g. Docker Compose cleanup)
     b. PixiOps(root).remove_packages() ← pixi remove
     c. after_pixi_remove()             ← hook
     d. ops.scaffold.cleanup_files()    ← delete generated files
     e. SecretsOps(root).remove()       ← delete secret files
     f. ops.scaffold.restore_originals()← restore templates from new/templates/
     g. TrackingOps(section).remove()   ← update djdevx.toml
```

The hook order is an invariant and must not change.

## Dev Services (pixi-native)

`services/` hosts long-running local dev services (Postgres, Redis, OTel
collector, OpenObserve). Each `BaseDevService` subclass declares a `category`
(`database` / `cache` / `otel`) and registers into `SERVICE_REGISTRY`;
resolvers in `services/registry.py` read `djdevx.toml` tracking and return the
installed services in deterministic order (postgres → redis → otel →
openobserve). `ddx dev` commands (`up`, `down`, `status`, `start`) and the
declarative pipeline in `cli/dev.py` drive these services. Readiness uses the
shared pid/port helpers in `core/process.py`, and binaries downloaded as
release artifacts are SHA256-verified in `services/binary.py`.

## Component Architecture

- [Installable System](installable-system.md) — Installable, Registry, models, orchestrator, scaffold, auto-discovery
- [Integration Protocol](integration.md) — Peer integration engine: `peer_pixi_packages`, hooks, peer templates
- [Package Architecture](package-architecture.md) — BasePackage, variants, install params, secret generators
- [Feature Architecture](feature-architecture.md) — BaseFeature, dependencies, variants
- [Framework Architecture](framework-architecture.md) — BaseFramework, CSS/JS injection
- [Database Architecture](database-architecture.md) — BaseDatabase, Docker Compose via hooks
- [Cache Architecture](cache-architecture.md) — BaseCache, Docker Compose via hooks
- [Creating an Installable](creating-an-installable.md) — Shared pattern, concepts, and how-to guides for all installable types
- [CLI Architecture](cli-architecture.md) — Command tree, entry points, conventions
- [Template System](template-system.md) — Jinja2 setup, rendering, template discovery
- [Pydantic Settings](pydantic-settings.md) — Source priority, SettingCollector, design rules
- [URL Architecture](url-architecture.md) — URL pattern auto-registration
- [Deployment Architecture](deployment-architecture.md) — BaseDeployPlugin, auto-generated CLI
- [Console Utilities](console.md) — PrintConsole, prompt wrappers, style guidelines
- [Testing](testing.md) — Test patterns and conventions
- [Code Standards](code-standards.md) — Coding conventions and style
- [CLI Full Manual](../cli/manual.md) — Auto-generated command reference

## User Guide

- [Getting Started](../user-guide/getting-started.md)
- [Managing Packages](../user-guide/managing-packages.md)
- [Managing Features](../user-guide/managing-features.md)
- [Database Management](../user-guide/databases.md)
- [Cache Management](../user-guide/caching.md)
- [Managing Settings](../user-guide/managing-settings.md)
- [Deployment](../user-guide/deployment.md)
