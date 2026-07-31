# Architecture

`djdevx` is a CLI tool built with [Typer](https://typer.tiangolo.com/) that
generates and manages Django projects. It uses Jinja2 templates for code
generation and pydantic-settings for configuration management.

## High-Level Design

```
CLI (Typer) ──► Orchestrator ──► Installable ──┬── PixiOps (install deps)
                    ▲                  │        ├── Scaffold (copy templates)
                    │                  │        ├── SecretsOps (generate secrets)
                    │                  │        └── TrackingOps (write djdevx.toml)
                    │                  │
              Auto-discovery ──── Registry ──► Concrete installable modules
```

The flow is: a CLI command is dispatched to the orchestrator, which resolves
dependencies, collects interactive parameters, and calls `Installable.add()`.
The installable delegates to `PixiOps` (dependency installation), `Scaffold`
(Jinja2 template rendering), `SecretsOps` (secret file generation), and
`TrackingOps` (state persistence in `djdevx.toml`). Concrete installables
(packages, features, frameworks, databases, caches) are auto-discovered via
`pkgutil.iter_modules` and registered into typed registries at startup.

## Shared Infrastructure — `utils/installable/`

All five installable categories share a common foundation:

| File | Purpose |
|------|---------|
| `types.py` | `InstallableConfig`, `InstallParam`, `Variant`, `InstallableKind`, `InstallableRef` — data contracts for all installables |
| `installable.py` | `Installable` — pydantic `BaseModel` with lifecycle hooks and add/remove logic |
| `registry.py` | `Registry[T]` — generic type registry with `@register` decorator |
| `discovery.py` | `discover_and_register()` — auto-imports modules to trigger `@register` |
| `orchestrator.py` | `add_installable()` / `remove_installable()` — dependency resolution, interactive variant selection, parameter collection |
| `scaffold.py` | `copy_templates()` / `cleanup_files()` / `restore_original_templates()` — template rendering and file lifecycle |
| `pixi_ops.py` | `PixiOps` — pixi package add/remove operations |
| `secrets.py` | `SecretsOps` — secret generation and cleanup |
| `tracking.py` | `TrackingOps` + standalone queries — `djdevx.toml` read/write |
| `resolver.py` | `resolve()` — resolves `InstallableRef` to a class via the appropriate registry |
| `list_table.py` | `build_list_table()` — shared Rich table renderer for `list` commands |

Each category extends `Installable` through a thin category-specific base class
(`BasePackage`, `BaseFeature`, `BaseFramework`, `BaseDatabase`, `BaseCache`)
that sets `section` and returns the correct registry.

## Type Hierarchy

```
InstallableConfig (pydantic BaseModel)    ← utils/installable/types.py
  ├── install_params, pixi_packages, needs, secret_generators...
  └── Variant                              ← extends InstallableConfig (adds required=True)
        └── Installable                    ← utils/installable/installable.py (adds lifecycle hooks)
              ├── BasePackage              ← packages/_base.py
              ├── BaseFeature              ← features/_base.py
              ├── BaseFramework            ← frameworks/_base.py (adds CSS/JS download)
              ├── BaseDatabase             ← database/_base.py
              └── BaseCache                ← cache/_base.py
```

### Type Organization

Shared data types that span multiple modules live in `utils/types/` as
dedicated modules named by domain:

| File | Contents |
|------|----------|
| `utils/types/pixi_types.py` | `PixiPackageSpec` — conda/pypi dependency spec |

Installable-specific types live in `utils/installable/types.py` — tightly
coupled to that subsystem and not needed outside it.

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
     e. scaffold.copy_templates()       ← Jinja2 render + copy
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
     d. scaffold.cleanup_files()        ← delete generated files
     e. SecretsOps(root).remove()       ← delete secret files
     f. scaffold.restore_originals()    ← restore templates from new/templates/
     g. TrackingOps(section).remove()   ← update djdevx.toml
```

## Component Architecture

- [Installable System](installable-system.md) — Installable, Registry, types, orchestrator, scaffold, auto-discovery
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
