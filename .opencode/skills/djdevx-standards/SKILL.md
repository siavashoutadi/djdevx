---
name: djdevx-standards
description: >
  Project-wide code standards and best practices for the djdevx Python project.
  Use this skill as a reference for coding style, technology stack, and conventions.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: coding-standards
---

## Technology Stack

- **Python >=3.13** — Core language
- **Typer** — CLI framework for command-line interfaces
- **Jinja2** — Template engine for code generation
- **pytest** (with pytest-xdist) — Testing framework
- **Rich** — Console output with styling (PrintConsole wrapper)
- **uv** — Python package manager and runner
- **tomlkit** — TOML read/write for config tracking
- **requests** — HTTP client
- **Ruff** — Linter and formatter (via pre-commit)
- **Hatchling** — Build system

## Project Structure

- **Source layout**: All package code lives under `djdevx/`
- **Tests mirror source**: `tests/` structure mirrors `djdevx/`
- **Sub-command modules**: Each sub-command is a directory with `__init__.py` exposing a `typer.Typer()` as `app`
- **CLI entry point**: `djdevx.main:app` with `ddx` as alias
- **Templates**: Jinja2 templates under `djdevx/templates/`, use `.j2` extension
- **Project config**: `.djdevx/config.toml` read by `ProjectConfig`

## Patterns & Conventions

### Package Architecture
- Every installable Django package inherits from `BasePackage` (in `djdevx/backend/django/packages/_base.py`)
- Declare class attributes: `name`, `packages`, `dev_packages`, `required_dependencies`, `install_params`, `secret_generators`, `files_to_remove`, `folders_to_remove`
- Paths are auto-derived from `__file__` via `PathDeriver`
- Hook lifecycle: `before_uv_install` / `after_uv_install` / `before_copy_templates` / `after_copy_templates` / etc.
- Module-level singleton pattern: `_pkg = PackageClass(__file__)` + `app = _pkg.app`
- Multi-provider packages (allauth, anymail, storages) use sub-package layout under a directory

### CLI Conventions
- Use Typer with `No_args_is_help=True` on all apps
- Nested sub-commands via `app.add_typer(sub_app)`
- Use `Annotated[type, typer.Option(...)]` for CLI parameters
- `InstallParam` dataclass for install parameters with optional `show_if` for conditional prompts
- Config vars and secrets declared as pydantic `AppBaseSettings` subclasses in settings templates (not inline in the package class)

### Template Conventions
- Templates use `.j2` extension (stripped on render)
- Directory and file names can contain Jinja2 expressions (rendered dynamically)
- Use `TemplateManager` (wraps Jinja2 `FileSystemLoader`)
- `copy_templates()` walks `source_dir.rglob("*")`, renders names and content
- Template dirs live under `djdevx/templates/django/<package_name>/`

### Testing Conventions
- Use `pytest` with markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Default run: `uv run pytest` (auto-parallel via `-n auto`, short tracebacks)
- Use `temp_dir` fixture (wraps `tmp_path`) for isolated filesystem tests
- Use `Typer CliRunner` for CLI integration tests
- Use `unittest.mock.patch` to isolate unit tests (e.g., mock `BasePackage._derive_djdevx_root`)
- Package integration tests live in `tests/backend/django/packages/test_<name>.py`
- Tracking output verified in `tests/.../test_tracking_configs.py`

### Config & Tracking
- Installed packages tracked under `.djdevx/backend/django/packages/<template_path>/config.toml`
- Trackers: `PackageTracker`, `FeatureTracker`, `DatabaseTracker`, `CacheTracker`
- `UvRunner` wraps `uv add`, `uv remove`, `uv run`, and Django manage.py commands
- `DjangoProjectManager` centralizes path, template, env var, and dependency operations
- `EnvFileManager` handles `.devcontainer/.env/` files
- Package names normalized per PEP 503 (hyphens vs underscores vs dots)

### Console Output
- Use `PrintConsole` singleton: `.step()` (cyan), `.success()` (green), `.error()` (red), `.info()` (plain), `.warning()` (yellow), `.list()` (bullets), `.diff()` (side-by-side)

### Code Quality
- All code formatted and linted with Ruff (via pre-commit)
- Extensive type hints required (including `Annotated` for Typer)
- Descriptive naming over comments — only comment complex logic
- Docstrings for all classes and functions
- Follow PEP 8
