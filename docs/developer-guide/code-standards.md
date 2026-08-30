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
  `conditional_packages`, `needs`, `variants`, `exclusive_variants`,
  `install_params`, `files_to_remove`, `folders_to_remove`,
  `restore_on_remove`, `secret_generators`
- Use `@register` decorator from the category's `_registry.py` — no manual
  `__init__.py` registration needed
- Names are normalized automatically — at construction (`InstallableConfig`,
  `Variant`, `InstallableRef`), registry lookup (`Registry.get()`), and in
  `add_installable()` / `remove_installable()`. Never call
  `InstallableConfig.normalize_name()` manually and never inline
  `.replace("_", "-")` at call sites
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

### Django Manage.py Commands

- Route Django `manage.py` commands through `ManageCommands`
  (`djdevx/utils/django/manage_commands.py`) — never call `pixi` directly from
  command modules
- `ManageCommands` owns a `PixiRunner` instance — its only dependency. Pass the
  shared runner in when one already exists, otherwise it builds its own:
  `ManageCommands(runner)`
- Expose one named method per `manage.py` command (e.g. `migrations_pending()`);
  the generic `run(command, *args, check=...)` is the low-level delegate to
  `PixiRunner.run_manage_command`
- New `manage.py` helpers belong in `manage_commands.py`, keeping command modules
  thin

```python
from djdevx.utils.django.manage_commands import ManageCommands

commands = ManageCommands(runner)  # or ManageCommands() for a default runner
if commands.migrations_pending():
    commands.run("migrate")
```

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
- `ProjectTracking` is the single tracking entry point — it owns the
  `djdevx.toml` document and provides section-scoped operations
- Sections are `Section` enum members (`Section.PACKAGES`, `Section.FEATURES`,
  `Section.FRAMEWORKS`, `Section.DATABASE`, `Section.CACHE`)
- `TrackingOps(section)` wraps `ProjectTracking` for the installable lifecycle
- `PixiOps` wraps `pixi add` / `pixi remove` for the installable lifecycle
- `PixiRunner` is the low-level pixi process runner; Django `manage.py` commands
  go through `ManageCommands` (see [Django Manage.py Commands](#django-managepy-commands))
- `Scaffold` centralizes path, template, and file operations — replaces the
  deprecated `DjangoProjectManager`
- Package names normalized per PEP 503 (hyphens vs underscores vs dots)
- `Registry[T]` provides generic type registration with name normalization

> Read the [Installable System](installable-system.md#tracking-system) for details on the tracking and registry system.

### Console Output

- Use `PrintConsole` singleton and prompt wrappers for all CLI output
- Use `prompts.*()` wrappers for interactive input — never use
  `typer.Option(prompt=...)`; make params `Optional[T]` with `None` default
  and prompt via questionary in the function body (see
  [Interactive Fallback Pattern](console.md#interactive-fallback-pattern))
- See [Console Utilities](console.md) for the full API and style guidelines

### Code Quality

- All code formatted and linted with Ruff (via prek)
- Extensive type hints required (including `Annotated` for Typer)
- Descriptive naming over comments — only comment complex logic
- Docstrings for all classes and functions
- Follow PEP 8
