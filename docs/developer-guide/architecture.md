# Architecture

`djdevx` is a CLI tool built with [Typer](https://typer.tiangolo.com/) that
generates and manages Django projects. It uses Jinja2 templates for code
generation and pydantic-settings for configuration management.

## High-Level Design

```
CLI (Typer) ──► Commands ──► Module ──┬── Install dependencies (pixi)
                  ▲              ├── Copy Jinja2 templates
                  │              ├── Append settings / URLs
                  │              └── Generate secrets
                  │
            .djdevx/ (read/write project state)
```

The flow is: a CLI command is dispatched to a module (package, feature, create,
or settings), which installs dependencies, copies Jinja2 templates into the
project, appends settings and URL patterns, and generates secrets. Modules
read and write project state through `.djdevx/`.

## Component Architecture

- [CLI Architecture](cli-architecture.md) -- Command tree, entry points, conventions
- [Package Architecture](package-architecture.md) -- BasePackage, lifecycle hooks, registration
- [Template System](template-system.md) -- Jinja2 setup, rendering, template discovery
- [Pydantic Settings](pydantic-settings.md) -- Source priority, SettingCollector, design rules
- [URL Architecture](url-architecture.md) -- URL pattern auto-registration
- [Deployment Architecture](deployment-architecture.md) -- BaseDeployPlugin, auto-generated CLI, adding targets
- [Feature Architecture](../user-guide/managing-features.md) -- High-level feature installation
- [Database Management](../user-guide/databases.md) -- PostgreSQL database management
- [Cache Management](../user-guide/caching.md) -- Redis cache management
- [Console Output](code-standards.md) -- Rich-based PrintConsole API
