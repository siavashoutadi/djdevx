# Getting Started

## Installation

Install `djdevx` using `uv`:

```bash
uv tool install git+https://github.com/siavashoutadi/djdevx
```

This installs two CLI entry points:

- `djdevx` -- full command name
- `ddx` -- shorthand alias

## Initialize a New Django Project

```bash
ddx new --project-name myproject --project-directory ./myproject
```

This scaffolds a complete Django project with:

- `.devcontainer/` -- VS Code devcontainer with Docker Compose
- `Dockerfile` -- Production-ready container image
- `docker-compose.yaml` -- Local development services
- `prek.toml` -- Linting and formatting hooks
- `pyproject.toml` -- Project metadata and dependencies
- `.env` template -- Environment variable management
- Pydantic-settings based configuration classes

## First Steps After Scaffolding

After the project is created, inspect what secrets and config vars the
project needs, then initialize and verify:

```bash
cd myproject
ddx settings secrets list dev
ddx settings configs list dev
ddx settings secrets init dev
ddx settings secrets verify dev
ddx settings configs verify dev
```

The `list` commands show every required field and its resolve source.
`init` generates local `.secrets/` files with safe dev defaults. `verify`
confirms everything is present before you start development.

## Navigate the Project

The scaffolded project uses `pixi` as its package manager:

```bash
cd myproject
pixi run python manage.py runserver
```

## Install a Package

From the project root directory:

```bash
ddx packages add whitenoise
```

This installs the `whitenoise` package, adds it to `INSTALLED_APPS`,
configures middleware, and sets up any required environment variables.

All `ddx` commands must be run from the project root directory (`myproject/`).

## Install a Database

```bash
ddx database add postgres
```

Only one database can be installed at a time. The command will block if
another database is already installed.

## Install a Cache

```bash
ddx cache add redis
```

Only one cache can be installed at a time.

## Explore Commands

```bash
ddx --help                 # Top-level help
```

## Command Cheat Sheet

| Task | Command |
|------|---------|
| New project | `ddx new --project-name <name>` |
| Add package | `ddx packages add <name>` |
| Remove package | `ddx packages remove <name>` |
| List packages | `ddx packages list` |
| Add framework | `ddx frameworks add <name>` |
| Add feature | `ddx features add <name>` |
| Add database | `ddx database add <name>` |
| Add cache | `ddx cache add <name>` |
| Create app | `ddx create app --name <name>` |
| Manage secrets | `ddx settings secrets {init,list,verify}` |
| Deploy | `ddx deployment docker-compose generate` |

## Next Steps

- [Managing Packages](managing-packages.md) -- Learn about the package system
- [Managing Features](managing-features.md) -- Add PWA and more
- [Database Management](databases.md) -- Set up databases
- [Cache Management](caching.md) -- Set up caches
- [Architecture Overview](../developer-guide/architecture.md) -- Understand how djdevx is built
- [CLI Full Manual](../cli/manual.md) -- Full command reference
