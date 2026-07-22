# Code Standards

## Technology Stack

- **Python >= 3.13** -- Core language
- **Typer** -- CLI framework for command-line interfaces
- **Jinja2** -- Template engine for code generation
- **pytest** (with pytest-xdist) -- Testing framework
- **Rich** -- Console output with styling (`PrintConsole` wrapper)
- **uv** -- Python package manager and runner
- **tomlkit** -- TOML read/write for config tracking
- **requests** -- HTTP client
- **Ruff** -- Linter and formatter (via prek)
- **Hatchling** -- Build system

> Read the [Architecture](architecture.md) for a high-level overview of how these components fit together.

## Project Structure

- **Source layout**: All package code lives under `djdevx/`
- **Tests mirror source**: `tests/` structure mirrors `djdevx/`
- **Sub-command groups**: Each group of related sub-commands is a directory with
  `__init__.py` exposing a `typer.Typer()` as `app`; standalone commands
  (`version`, `requirement`) are single-file modules
- **CLI entry point**: `djdevx.main:app` with `ddx` as alias
- **Templates**: Jinja2 templates under `djdevx/templates/`, use `.j2` extension
- **Project config**: `.djdevx/config.toml` read by `ProjectConfig`

> Read the [CLI Architecture](cli-architecture.md) for the full command tree and entry point details.

## Patterns & Conventions

### Package Architecture

- Every installable Django package inherits from `BasePackage`
  (`djdevx/backend/django/packages/_base.py`)
- Declare class attributes: `name`, `packages`, `dev_packages`,
  `required_dependencies`, `install_params`, `secret_generators`,
  `files_to_remove`, `folders_to_remove`
- Paths are auto-derived from `__file__` via `PathDeriver`
- Hook lifecycle: `before_uv_install` / `after_uv_install` /
  `before_copy_templates` / `after_copy_templates` / etc.
- Module-level singleton pattern: `_pkg = PackageClass(__file__)` +
  `app = _pkg.app`
- Multi-provider packages (allauth, anymail, storages) use sub-package layout
  under a directory

> Read the [Package Architecture](package-architecture.md) for detailed documentation on BasePackage, lifecycle hooks, path derivation, and registration.

### CLI Conventions

- Use Typer with `no_args_is_help=True` on all apps
- Nested sub-commands via `app.add_typer(sub_app)`
- Use `Annotated[type, typer.Option(...)]` or bare `typer.Option(...)` for CLI
  parameters
- `InstallParam` dataclass for install parameters with optional `show_if` for
  conditional prompts
- Config vars and secrets declared as pydantic `AppBaseSettings` subclasses in
  settings templates (not inline in the package class)

> Read the [CLI Architecture](cli-architecture.md) for detailed CLI conventions and patterns.

### Template Conventions

- Templates use `.j2` extension (stripped on render)
- Directory and file names can contain Jinja2 expressions (rendered
  dynamically)
- Use `TemplateManager` (wraps Jinja2 `FileSystemLoader`)
- `copy_templates()` walks `source_dir.rglob("*")`, renders names and content
- Template dirs live under `djdevx/templates/django/<package_name>/`

> Read the [Template System](template-system.md) for detailed rendering and template discovery documentation.

### Testing Conventions

- Use `pytest` (markers available: `@pytest.mark.unit`,
  `@pytest.mark.integration`, `@pytest.mark.slow`)
- Default run: `uv run pytest` (auto-parallel via `-n auto`, short tracebacks)
- Use `temp_dir` fixture (wraps `tmp_path`) for isolated filesystem tests
- Use `Typer CliRunner` for CLI integration tests
- Use `unittest.mock.patch` to isolate unit tests (e.g., mock
  `BasePackage._derive_djdevx_root`)
- Package integration tests live in
  `tests/backend/django/packages/test_<name>.py`
- Tracking output verified in
  `tests/backend/django/test_tracking_configs.py`

> Read the [Testing Guide](testing.md) for detailed testing instructions and patterns.

### Config & Tracking

- Installed packages tracked under
  `.djdevx/backend/django/packages/<template_path>/config.toml`
- Trackers: `PackageTracker`, `FeatureTracker`, `DatabaseTracker`,
  `CacheTracker`
- `UvRunner` wraps `uv add`, `uv remove`, `uv run`, and Django manage.py
  commands
- `DjangoProjectManager` centralizes path, template, env var, and dependency
  operations
- Package names normalized per PEP 503 (hyphens vs underscores vs dots)

> Read the [Package Architecture](package-architecture.md#package-tracking) for details on the tracking system.

### Console Output

- Use `PrintConsole` singleton: `.step()` (cyan), `.success()` (green),
  `.error()` (red), `.info()` (plain), `.warning()` (yellow), `.list()`
  (bullets), `.diff()` (side-by-side)

### Code Quality

- All code formatted and linted with Ruff (via prek)
- Extensive type hints required (including `Annotated` for Typer)
- Descriptive naming over comments -- only comment complex logic
- Docstrings for all classes and functions
- Follow PEP 8
