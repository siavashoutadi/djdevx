# Code Standards

## Technology Stack

- **Python >= 3.13** — Core language
- **Typer** — CLI framework for command-line interfaces
- **Jinja2** — Template engine for code generation
- **pytest** (with pytest-xdist) — Testing framework
- **Rich** — Console output with styling (`PrintConsole` wrapper)
- **pixi** — Python package manager and runner
- **tomlkit** — TOML read/write for config tracking
- **requests** — HTTP client
- **Ruff** — Linter and formatter (via prek)
- **Hatchling** — Build system

> Read the [Architecture](architecture.md) for a high-level overview of how these components fit together.

## Project Structure

- **Source layout**: All package code lives under `djdevx/`
- **Tests mirror source**: `tests/` structure mirrors `djdevx/`
- **Sub-command groups**: Each group of related commands is a directory with
  `__init__.py` exposing a `typer.Typer()` as `app`; standalone commands
  (`version`, `requirement`) are single-file modules
- Installable categories (`packages/`, `features/`, `frameworks/`, `database/`,
  `cache/`) follow the split pattern: `__init__.py` (typer app +
  auto-discovery), `_base.py` (base class extending `Installable`),
  `_registry.py` (Registry instance), `add.py`/`remove.py`/`list.py` (CLI commands)
- Each concrete installable lives in its own subdirectory with an
  `@register`-decorated class extending the category base
- **Shared types**: cross-module data types in `utils/types/` (e.g. `pixi_types.py`); module-specific types stay local (e.g. `utils/installable/types.py`)
- **CLI entry point**: `djdevx.main:app` with `ddx` as alias
- **Templates**: Jinja2 templates inside each installable's `templates/` folder,
  use `.jinja2` extension (stripped on render)
- **Project config**: `.project/ddx/config.toml` read by `ProjectConfig`

> Read the [CLI Architecture](cli-architecture.md) for the full command tree and entry point details.

## Patterns & Conventions

### Package Architecture

- Every installable component inherits from a category-specific base class
  extending `Installable` (`djdevx/utils/installable/base.py`)
- Five categories: packages (`BasePackage`), features (`BaseFeature`),
  frameworks (`BaseFramework`), database (`BaseDatabase`), cache (`BaseCache`)
- Declare class attributes: `name`, `display_name`, `pixi_packages`,
  `needs`, `variants`, `exclusive_variants`, `install_params`,
  `files_to_remove`, `folders_to_remove`, `restore_on_remove`,
  `secret_generators`
- Use `@register` decorator from the category's `_registry.py` — no manual
  `__init__.py` registration needed
- Auto-discovery via `discover_and_register()` in each category's `__init__.py`,
  or `pkgutil.iter_modules` with `_internal` set to skip infrastructure files
- Each category implements `get_registry()` and `get_tracking_cls()` class
  methods to power shared discovery and autocomplete
- Hook lifecycle: `before_pixi_install` / `after_pixi_install` /
  `before_copy_templates` / `after_copy_templates` / `before_pixi_remove` /
  `after_pixi_remove` — do **not** override `install()` or `remove()` directly
- CLI commands split into `add.py`, `remove.py`, `list.py` per category
- `list.py` uses shared `build_list_table(cls, label)` from
  `utils/installable/list_table.py`
- Variants use `list[PixiPackageSpec]` for dependencies (not `list[str]`);
  set `pixi_feature="dev"` for dev-only packages

> Read the [Package Architecture](package-architecture.md),
> [Feature Architecture](feature-architecture.md),
> [Framework Architecture](framework-architecture.md),
> [Database Architecture](database-architecture.md),
> [Cache Architecture](cache-architecture.md), and
> [Installable System](installable-system.md) for detailed documentation.

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

- Templates use `.jinja2` extension (stripped on render)
- Directory and file names can contain Jinja2 expressions (rendered dynamically)
- Use `Scaffold` (wraps Jinja2 `FileSystemLoader`) — replaces the deprecated
  `TemplateManager`
- `scaffold.copy_templates()` renders templates from the installable's
  `templates/` directory to the project
- Template dirs live under each installable's `templates/` folder, not in a
  central location

> Read the [Template System](template-system.md) for detailed rendering and template discovery documentation.

### Testing Conventions

- Use `pytest` (markers available: `@pytest.mark.unit`,
  `@pytest.mark.integration`, `@pytest.mark.slow`)
- Default run: `pixi run pytest` (auto-parallel via `-n auto`, short tracebacks)
- Use `temp_dir` fixture (wraps `tmp_path`) for isolated filesystem tests
- Use `Typer CliRunner` for CLI integration tests
- Package integration tests follow the source directory structure under
  `tests/packages/`

> Read the [Testing Guide](testing.md) for detailed testing instructions and patterns.

### Config & Tracking

- Installed items tracked in `djdevx.toml` under category-specific sections:
  `[packages]`, `[features]`, `[frameworks]`, `[database]`, `[cache]`
- Trackers: `PackageTracking`, `FeatureTracking`, `FrameworkTracking`,
  `DatabaseTracking`, `CacheTracking` (all extend `SectionTracking`)
- `PixiOps` wraps `pixi add`, `pixi remove`, `pixi run`, and Django manage.py
  commands — replaces the deprecated `PixiRunner`
- `Scaffold` centralizes path, template, and file operations — replaces the
  deprecated `DjangoProjectManager`
- Package names normalized per PEP 503 (hyphens vs underscores vs dots)
- `Registry[T]` provides generic type registration with name normalization

> Read the [Installable System](installable-system.md#tracking-system) for details on the tracking and registry system.

### Console Output

- Use `PrintConsole` singleton and prompt wrappers for all CLI output
- See [Console Utilities](console.md) for the full API and style guidelines

### Code Quality

- All code formatted and linted with Ruff (via prek)
- Extensive type hints required (including `Annotated` for Typer)
- Descriptive naming over comments — only comment complex logic
- Docstrings for all classes and functions
- Follow PEP 8
