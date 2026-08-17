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

After the project is created, start the local development environment with a
single command:

```bash
cd myproject
ddx dev start
```

This handles everything automatically:

- initializes dev configs and secrets
- starts the dev database and cache natively (if installed) and applies
  pending migrations
- runs the dev server in the foreground

`ddx dev start` is idempotent — running it again just starts whatever is
missing and runs the server. See [Local Development](dev.md) for the full
command reference.

## Navigate the Project

The scaffolded project uses `pixi` as its package manager. Instead of running
the server manually, use:

```bash
ddx dev start
```

or, to only run the server without any checks:

```bash
ddx dev runserver
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
| Start dev environment | `ddx dev start` |
| Run dev server only | `ddx dev runserver` |
| Dev service status | `ddx dev status` |
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

- [Local Development](dev.md) -- Run the dev environment natively with pixi
- [Managing Packages](managing-packages.md) -- Learn about the package system
- [Managing Features](managing-features.md) -- Add PWA and more
- [Database Management](databases.md) -- Set up databases
- [Cache Management](caching.md) -- Set up caches
- [Architecture Overview](../developer-guide/architecture.md) -- Understand how djdevx is built
- [CLI Full Manual](../cli/manual.md) -- Full command reference
