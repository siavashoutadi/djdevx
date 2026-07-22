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
ddx new backend django --project-name myproject --project-directory ./myproject
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
ddx backend django settings secrets list dev
ddx backend django settings configs list dev
ddx backend django settings secrets init dev
ddx backend django settings secrets verify dev
ddx backend django settings configs verify dev
```

The `list` commands show every required field and its resolve source.
`init` generates local `.secrets/` files with safe dev defaults. `verify`
confirms everything is present before you start development.

## Navigate the Project

The scaffolded project uses `pixi` as its package manager. Navigate to the
backend directory and start the development server:

```bash
cd backend
pixi run python manage.py runserver
```

## Install a Package

From the project root directory:

```bash
ddx backend django packages whitenoise install
```

This installs the `whitenoise` package, adds it to `INSTALLED_APPS`,
configures middleware, and sets up any required environment variables.

Note that all `ddx` commands must be run from the project root directory
(`myproject/`), not from `backend/`.

## Explore Commands

```bash
ddx --help                 # Top-level help
ddx backend django --help  # Django-specific commands
```

## Next Steps

- [Architecture Overview](../developer-guide/architecture.md) -- Understand how djdevx is built
- [CLI Full Manual](../cli/manual.md) -- Full command reference
- [Package Management](managing-packages.md) -- Learn about the package system
