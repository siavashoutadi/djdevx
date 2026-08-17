# djdevx

**Supercharge Your Django Development Workflow**

`djdevx` is a powerful command-line tool designed to enhance the productivity
and experience of Django developers. It provides a suite of features to
streamline your workflow and make development enjoyable.

## Key Features

- **Simplified Project Setup** — Quickly scaffold Django applications with best
  practices, including devcontainer, Docker, prek, and environment
  management out of the box.
- **Package Management** — Install and configure 39+ popular Django packages
  (`django-allauth`, `djangorestframework`, `django-debug-toolbar`, `channels`,
  and more) with a single command.
- **Feature Addition** — Add PWA support, CSS frameworks (Bootstrap, FrankenUI,
  Semantic, Starting Point UI), and deployment configurations.
- **Database Management** — Create and manage databases with support for
  multiple providers, devcontainer integration, and single-instance enforcement.
- **Cache Management** — Create and manage cache backends with support for
  multiple providers and devcontainer integration.
- **Secrets & Configuration** — Manage environment variables, secrets, and
  settings across dev and production environments using pydantic-settings.
- **Customizable Templates** — Leverage pre-configured Jinja2 templates for
  common Django use cases.
- **Shell Autocompletion** — Tab-complete package, feature, framework, database,
  and cache names on add/remove commands.

## Quick Start

```bash
uv tool install git+https://github.com/siavashoutadi/djdevx
ddx new --project-name myproject
cd myproject
ddx packages add whitenoise
```

## User Guide

| Section | Description |
|---------|-------------|
| [Getting Started](user-guide/getting-started.md) | Install, scaffold, and configure your first project |
| [Managing Packages](user-guide/managing-packages.md) | Install and manage Django packages |
| [Managing Features](user-guide/managing-features.md) | Add PWA support and CSS frameworks |
| [Database](user-guide/databases.md) | Create and manage databases |
| [Cache](user-guide/caching.md) | Create and manage caches |
| [Local Development](user-guide/dev.md) | Run the dev environment natively with pixi |
| [Managing Settings](user-guide/managing-settings.md) | Configure secrets, config vars, and environment |
| [Content Security Policy](user-guide/content-security-policy.md) | Configure strict CSP defaults, directives, and nonces |
| [Deployment](user-guide/deployment.md) | Generate Docker Compose / Kubernetes manifests |
| [CLI Full Manual](cli/manual.md) | Auto-generated command reference |

## Developer Guide

| Section | Description |
|---------|-------------|
| [Architecture](developer-guide/architecture.md) | High-level system design |
| [CLI Architecture](developer-guide/cli-architecture.md) | Command tree, Typer conventions |
| [Installable System](developer-guide/installable-system.md) | Installable, Registry, tracking, auto-discovery |
| [Package Architecture](developer-guide/package-architecture.md) | BasePackage, lifecycle, variants, templates |
| [Creating an Installable](developer-guide/creating-an-installable.md) | Shared pattern, variants, params, hooks, templates, testing |
| [Add a Package](developer-guide/adding-a-package.md) | How-to: packages, variants, secrets, hooks |
| [Add a Feature](developer-guide/adding-a-feature.md) | How-to: features and dependencies on packages |
| [Add a Framework](developer-guide/adding-a-framework.md) | How-to: CSS/JS frameworks |
| [Add a Database](developer-guide/adding-a-database.md) | How-to: database providers |
| [Add a Cache](developer-guide/adding-a-cache.md) | How-to: cache providers |
| [Template System](developer-guide/template-system.md) | Jinja2 rendering |
| [Pydantic Settings](developer-guide/pydantic-settings.md) | Settings architecture and SettingCollector |
| [URL Architecture](developer-guide/url-architecture.md) | URL auto-registration |
| [Testing](developer-guide/testing.md) | Test patterns and conventions |
| [Code Standards](developer-guide/code-standards.md) | Coding conventions and style |

## License

`djdevx` is open-source software licensed under the [MIT License](https://github.com/siavashoutadi/djdevx/blob/main/LICENSE).
