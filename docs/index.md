# djdevx

**Supercharge Your Django Development Workflow**

`djdevx` is a powerful command-line tool designed to enhance the productivity
and experience of Django developers. It provides a suite of features to
streamline your workflow and make development enjoyable.

## Key Features

- **Simplified Project Setup** -- Quickly scaffold Django applications with best
  practices, including devcontainer, Docker, pre-commit, and environment
  management out of the box.
- **Package Management** -- Install and configure 30+ popular Django packages
  (`django-allauth`, `djangorestframework`, `django-debug-toolbar`, `channels`,
  and more) with a single command.
- **Feature Addition** -- Add PWA support, CSS frameworks (Bootstrap, FrankenUI,
  Semantic, Starting Point UI), Tailwind themes, and deployment configurations.
- **Database Management** -- Create and manage PostgreSQL databases for your
  Django projects.
- **Cache Management** -- Create and manage Redis caches for your Django
  projects.
- **Secrets & Configuration** -- Manage environment variables, secrets, and
  settings across dev and production environments using pydantic-settings.
- **Customizable Templates** -- Leverage pre-configured Jinja2 templates for
  common Django use cases.

## Quick Start

```bash
uv tool install git+https://github.com/siavashoutadi/djdevx
ddx init
ddx --help
```

## User Guide

| Section | Description |
|---------|-------------|
| [Getting Started](user-guide/getting-started.md) | Install, scaffold, and configure your first project |
| [Managing Packages](user-guide/managing-packages.md) | Install and manage Django packages |
| [Managing Features](user-guide/managing-features.md) | Add PWA support and CSS frameworks |
| [Database](user-guide/databases.md) | Create and manage PostgreSQL databases |
| [Cache](user-guide/caching.md) | Create and manage Redis caches |
| [Managing Settings](user-guide/managing-settings.md) | Configure secrets, config vars, and environment |
| [CLI Architecture](developer-guide/cli-architecture.md) | Command tree, Typer conventions, adding sub-commands |
| [CLI Full Manual](cli/manual.md) | Auto-generated command reference |

## Developer Guide

| Section | Description |
|---------|-------------|
| [Architecture](developer-guide/architecture.md) | High-level system design |
| [Package Architecture](developer-guide/package-architecture.md) | BasePackage, lifecycle, registration |
| [Template System](developer-guide/template-system.md) | Jinja2 rendering |
| [Pydantic Settings](developer-guide/pydantic-settings.md) | Settings architecture and SettingCollector |
| [URL Architecture](developer-guide/url-architecture.md) | URL auto-registration |
| [Creating a Package](developer-guide/creating-a-package.md) | Step-by-step guide |
| [Testing](developer-guide/testing.md) | Test patterns and conventions |
| [Code Standards](developer-guide/code-standards.md) | Coding conventions and style |

## License

`djdevx` is open-source software licensed under the [MIT License](https://github.com/siavashoutadi/djdevx/blob/main/LICENSE).
