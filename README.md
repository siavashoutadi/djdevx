# `djdevx`

## Supercharge Your Django Development Workflow

`djdevx` is a powerful command-line tool designed to enhance the productivity and experience of Django developers. `djdevx` provides a suite of features to streamline your workflow and make development enjoyable.

### Key Features

- **Simplified Project Setup**: Quickly scaffold Django applications with best practices.
- **Enhanced Debugging Tools**: Integrate popular debugging packages effortlessly.
- **Customizable Templates**: Leverage pre-configured templates for common Django use cases.
- **Optimized Developer Experience**: Automate repetitive tasks and focus on writing great code.

### Why Choose `djdevx`?

- **Complete Project Scaffolding**: `ddx new` generates a best-practice Django project — devcontainer, `Dockerfile`, `docker-compose.yaml`, `prek.toml`, `pyproject.toml`, and pydantic-settings based configuration — ready from the first command.
- **One-Command Package Setup**: Install and configure 39+ Django packages (`django-allauth`, `django-debug-toolbar`, `djangorestframework`, and more) that wire up dependencies, `INSTALLED_APPS`, middleware, settings, URL patterns, and templates for you.
- **Features Beyond Packages**: Add high-level features like PWA support, CSS frameworks (Bootstrap, FrankenUI, Semantic, Starting Point UI), and Tailwind themes that span multiple packages and configuration changes.
- **Databases & Caches**: Set up PostgreSQL and Redis with devcontainer and Docker Compose integration via `ddx database add postgres` and `ddx cache add redis`.
- **Typed Configuration**: pydantic-settings based config with automatic discovery across app, package, and core settings. `ddx settings` lists, initializes, and verifies secrets and config vars for dev and prod.
- **Secrets Done Right**: Secrets live in `.secrets/` (never committed), config vars in `.env`. Dev mode auto-generates safe defaults; prod mode prompts for every value and fails verification if anything is missing.
- **Production Deployment Generation**: Generate Docker Compose manifests with Traefik reverse-proxy and Let's Encrypt, then verify everything is in place before deploying.
- **Clean Lifecycle, Clean Removal**: State is tracked in `djdevx.toml`; removing anything uninstalls its dependencies, deletes generated files, and restores originals.
- **Shell Autocompletion**: Tab-complete package, feature, framework, database, and cache names.
- **Developer-First Environment**: pixi-based dependencies, prek linting/formatting hooks, and devcontainer support keep every developer on a consistent, portable setup.

### Quick Start

```bash
# Install djdevx
uv tool install git+https://github.com/siavashoutadi/djdevx

# Scaffold a new Django project
ddx new --project-name myproject
cd myproject

# Install and configure a package, for example, whitenoise
ddx packages add whitenoise
```

This installs two CLI entry points: `djdevx` and its shorthand alias `ddx`.
Explore all available commands with `ddx --help`.

### Documentation

For the full user guide, command reference, and developer documentation, visit the [documentation website](https://siavashoutadi.github.io/djdevx/).

### License

`djdevx` is open-source software licensed under the [MIT License](LICENSE).

---

Boost your Django development experience with `djdevx` today!
