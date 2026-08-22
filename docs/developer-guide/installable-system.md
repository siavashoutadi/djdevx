# Installable System

All five installable categories (packages, frameworks, features, databases,
caches) share a common architecture. This document explains the shared
infrastructure that powers them all.

## Directory Structure

```
utils/installable/
├── __init__.py           # Re-exports Installable, Registry, InstallParam, Variant, discover_and_register, build_list_table
├── types.py              # InstallableConfig, InstallParam, Variant, InstallableKind, InstallableRef
├── installable.py        # Installable — pydantic BaseModel, add/remove lifecycle, hooks
├── registry.py           # Registry[T] — generic type registry with @register
├── discovery.py          # discover_and_register() — auto-import modules to trigger @register
├── orchestrator.py       # add_installable() / remove_installable() — dependency resolution, interactive selection, parameter collection
├── scaffold.py           # copy_templates() / cleanup_files() / restore_original_templates()
├── pixi_ops.py           # PixiOps — pixi package add/remove
├── secrets.py            # SecretsOps — secret generation and cleanup
├── tracking.py           # TrackingOps + standalone queries (get_installed_names, autocomplete, etc.)
├── resolver.py           # resolve() — resolves InstallableRef → class via registry
└── list_table.py         # build_list_table() — shared Rich table renderer
```

Each category has its own directory following this pattern:

```
<category>/
├── __init__.py           # typer.Typer() + auto-discovery + command registration
├── _base.py              # Base<Category>(Installable)
├── _registry.py          # Registry instance + convenience bindings
├── add.py                # add() command (calls orchestrator)
├── remove.py             # remove() command (calls orchestrator)
├── list.py               # list table via build_list_table()
└── <item>/               # Concrete installable modules (auto-discovered)
    ├── __init__.py       # @register decorated class
    └── templates/        # Jinja2 templates (optional)
```

## Data Types — `types.py`

### InstallableKind

A frozen dataclass identifying which category an installable belongs to. Five
singletons:

```python
PACKAGE = InstallableKind("package", "packages")
FEATURE = InstallableKind("feature", "features")
FRAMEWORK = InstallableKind("framework", "frameworks")
DATABASE = InstallableKind("database", "database")
CACHE = InstallableKind("cache", "cache")
```

### InstallableRef

A reference `(name, kind)` used for dependency declarations (the `needs`
field). Resolved at install time by `resolver.py`:

```python
@dataclass
class InstallableRef:
    name: str
    kind: InstallableKind
```

### InstallParam

Declares a CLI parameter collected during add and passed to templates:

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Key in template context dict and CLI prompt |
| `type_` | `type` | Python type (default `str`) |
| `default` | `Any` | Default value |
| `help` | `str` | Help text |
| `prompt` | `Optional[str]` | If set, prompts user interactively |
| `show_if` | `Optional[str]` | Only prompt if this other param is truthy |
| `message_before_prompt` | `Optional[str]` | Message printed before the prompt |
| `hide_input` | `bool` | Use password input (hidden) |

### ConditionalPackage

A single pixi package guarded by an arbitrary condition:

```python
ConditionalCheck = Callable[..., bool]

@dataclass(frozen=True)
class ConditionalPackage:
    package: PixiPackageSpec
    when: ConditionalCheck
```

`when` is called with the owning installable instance as its first positional
argument (`when(installable)`). Return `True` to include the package, `False`
to skip it. Evaluated by `Installable.add()`/`remove()` via
`_active_conditional_packages()`. Use an unbound method reference to read
instance state, or a lambda taking one parameter.

### InstallableConfig

The shared pydantic `BaseModel` that all installables extend:

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier (underscores normalized to hyphens) |
| `display_name` | `str` | Human-readable name for CLI output |
| `pixi_packages` | `list[PixiPackageSpec]` | PyPI/conda packages (set `pixi_feature="dev"` for dev-only) |
| `conditional_packages` | `list[ConditionalPackage]` | Pixi packages installed only when their `when(installable)` condition holds |
| `template_path` | `str` | Override auto-derived template directory |
| `install_params` | `list[InstallParam]` | Parameters collected at install time |
| `needs` | `list[InstallableRef]` | Dependencies that must be installed first |
| `secret_generators` | `dict[str, Callable]` | Maps field names to generator callables |
| `files_to_remove` | `list[str]` | Files to delete on uninstall |
| `folders_to_remove` | `list[str]` | Folders to delete on uninstall |
| `restore_on_remove` | `dict[str, str]` | Template overrides (project_rel → template_rel) |

### Variant

A `Variant` extends `InstallableConfig` with one additional field:

| Attribute | Type | Description |
|-----------|------|-------------|
| `required` | `bool` | Auto-installed when the parent is added |

Represents a sub-option within an installable (e.g. "brevo" for anymail,
"account" for allauth, "s3" for storages).

## Installable — `installable.py`

`Installable` is a pydantic `BaseModel` extending `InstallableConfig` with
lifecycle hooks and add/remove logic.

### Additional Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `description` | `str` | Longer description |
| `section` | `str` | Tracking section name (set by category base class) |
| `exclusive_variants` | `bool` | If `True`, user picks exactly one variant |
| `variants` | `dict[str, Variant]` | Named variants |
| `verbose` | `bool` | Show full pixi output |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `structure` | `ProjectStructure` | Project path and structure helpers |
| `template_dir` | `Path` | Auto-derived from `inspect.getfile(self.__class__)` |
| `new_templates_dir` | `Path` | Project scaffold templates directory (`new/templates/`) |

### Install Lifecycle

```
add(variant_name, install_kwargs):
  1. before_pixi_install()                   ← hook
  2. PixiOps(root).add_packages(packages, variant)  ← pixi add
  3. PixiOps(root).add_packages(conditional)  ← conditional packages whose when(self) is True
  4. after_pixi_install()                    ← hook (e.g. Docker Compose config)
  5. before_copy_templates()                 ← hook
  6. scaffold.copy_templates(installable, variant)  ← Jinja2 rendering + copy
  7. after_copy_templates()                  ← hook (e.g. CSS download, icon gen)
  8. SecretsOps(root).generate(installable, variant)  ← auto-generate secret files
  9. TrackingOps(section).track_install(installable, variant)  ← write djdevx.toml
```

### Remove Lifecycle

```
remove(variant_name):
  1. before_pixi_remove()                    ← hook (e.g. Docker Compose cleanup)
  2. PixiOps(root).remove_packages(packages, variant)  ← pixi remove
  3. PixiOps(root).remove_packages(conditional)  ← conditional packages whose when(self) still holds
  4. after_pixi_remove()                     ← hook
  5. scaffold.cleanup_files(installable, variant)  ← delete generated files
  6. SecretsOps(root).remove(installable, variant)  ← delete secret files
  7. scaffold.restore_original_templates(installable)  ← restore originals
  8. TrackingOps(section).remove(name)       ← update djdevx.toml
```

### Lifecycle Hooks

Override these in subclasses for custom behavior:

| Hook | Timing |
|------|--------|
| `before_pixi_install()` | Before running `pixi add` |
| `after_pixi_install()` | After running `pixi add` |
| `before_copy_templates()` | Before copying template files |
| `after_copy_templates()` | After copying template files |
| `before_pixi_remove()` | Before running `pixi remove` |
| `after_pixi_remove()` | After running `pixi remove` |

Hooks can access install-time parameter values via `self._install_context`.

### Class Methods (Discovery)

Each category base class must implement these two:

```python
@classmethod
def get_registry(cls):
    """Return the Registry instance for this category."""
    raise NotImplementedError
```

All other discovery methods are provided by standalone functions in
`tracking.py`:

| Function | Returns | Description |
|----------|---------|-------------|
| `get_available_names(cls)` | `list[str]` | All registered items |
| `get_installed_names(cls)` | `dict` | Installed items from tracking |
| `get_installable_names(cls)` | `list[str]` | Available but not installed |
| `get_installed_variants(cls, name)` | `list[str]` | Installed variants for a given item |
| `get_display_name(cls, name)` | `str` | Human-readable name |
| `autocomplete_installable(cls, incomplete)` | `list[str]` | For CLI add autocomplete |
| `autocomplete_installed(cls, incomplete)` | `list[str]` | For CLI remove autocomplete |

## Registry — `registry.py`

`Registry[T]` is a generic type registry keyed by normalized name
(underscores → hyphens).

```python
from djdevx.utils.installable import Registry

MY_REGISTRY: Registry[BaseThing] = Registry(KIND)
register = MY_REGISTRY.register  # decorator
get_thing = MY_REGISTRY.get       # name → class
list_things = MY_REGISTRY.list    # sorted names
```

- `register(cls)` — stores the class under `cls.name` (normalizes underscores to hyphens)
- `get(name)` — returns the class or raises `KeyError` with available items listed
- `list()` — returns sorted name strings
- `values()` — returns the class objects

Each category instantiates its own `Registry` in `_registry.py`:

```python
from ..utils.installable import Registry
from ._base import BaseFramework

FRAMEWORK_REGISTRY: Registry[BaseFramework] = Registry(FRAMEWORK)
register = FRAMEWORK_REGISTRY.register
get_framework = FRAMEWORK_REGISTRY.get
list_frameworks = FRAMEWORK_REGISTRY.list
```

The `register` decorator is used on concrete classes:

```python
from .._base import BaseFramework
from .._registry import register

@register
class BootstrapFramework(BaseFramework):
    name: str = "bootstrap"
    ...
```

No manual registration in `__init__.py` is needed — `discover_and_register()`
handles it.

## Auto-Discovery — `discovery.py`

When any category's `__init__.py` is imported, `discover_and_register()` runs
and imports every concrete module via `pkgutil.iter_modules`:

```python
def discover_and_register(search_path, package_name):
    _skip = {"add", "remove", "list", "types"}
    for _, name, _ispkg in pkgutil.iter_modules(search_path, package_name + "."):
        short = name.rsplit(".", 1)[-1]
        if short.startswith("_") or short in _skip:
            continue
        importlib.import_module(name)
```

- Modules starting with `_` (internal) and command modules (`add`, `remove`,
  `list`, `types`) are skipped.
- Import errors are silently caught — an optional dependency being missing
  doesn't crash the CLI.

## Orchestrator — `orchestrator.py`

The orchestrator provides the centralized `add_installable()` and
`remove_installable()` functions that handle:

- **Dependency resolution** (`_auto_install_needs`) — recursively installs
  unmet `needs` before the target installable.
- **Variant selection** — three modes:
  - **Simple** — no variants, just install
  - **Exclusive variants** — choose exactly one (database provider, cache
    backend, storage backend)
  - **Additive variants** — pick multiple optional sub-features (allauth's
    account + mfa + oidc)
- **Interactive parameter collection** — prompts for `InstallParam` values
  via questionary. Supports `show_if` conditional prompts and
  `hide_input` for passwords.
- **`-p / --provider` flag** — non-interactive variant selection for scripting.
- **Multi-select mode** — batch add/remove with error skipping.

### Variant Behavior

- `exclusive_variants=True` — user picks exactly one variant (e.g. storage backends)
- `exclusive_variants=False` — variants can be combined (e.g. allauth features)
- `required=True` on a variant — auto-installed when the parent is added
- Removing the last additive variant removes the entire installable

## Scaffold — `scaffold.py`

Handles template rendering and file lifecycle for installables.

| Function | Description |
|----------|-------------|
| `resolve_template_source(installable, variant)` | Finds the correct template directory |
| `copy_templates(installable, variant)` | Renders and copies templates via `TemplateManager` |
| `template_output_files(installable, variant)` | Scans what files would be created (no I/O) |
| `cleanup_files(installable, variant)` | Deletes generated files and extra files/folders |
| `restore_original_templates(installable)` | Restores originals from `new/templates/` |
| `remove_empty_parents(root, path)` | Cleans up empty parent directories |

## PixiOps — `pixi_ops.py`

Wraps `PixiRunner` for package management operations:

```python
PixiOps(project_root, verbose).add_packages(packages, variant)
PixiOps(project_root, verbose).remove_packages(packages, variant)
```

Adds/removes pixi packages from the installable and its active variant.

## SecretsOps — `secrets.py`

Manages secret file lifecycle:

```python
SecretsOps(project_root).generate(installable, variant)  # auto-generate secrets
SecretsOps(project_root).remove(installable, variant)    # remove secret files
```

For each field in `secret_generators`, generates a value via the callable and
writes it to `.secrets/<field_name>` (or removes it).

## Tracking System

### ProjectTracking

`ProjectTracking` is the single tracking entry point. It owns the `djdevx.toml`
document (load/save) and reads/writes `[<section>.<name>]` entries via
`add()`, `remove()`, `is_installed()`, `get_variants()`, and `list()`.
Sections are `Section` enum members (`Section.PACKAGES`, `Section.FEATURES`,
`Section.FRAMEWORKS`, `Section.DATABASE`, `Section.CACHE`):

```python
project = ProjectTracking()
project.is_installed(Section.PACKAGES, "whitenoise")
project.add(Section.PACKAGES, "whitenoise", "Whitenoise")
project.remove(Section.PACKAGES, "whitenoise")
project.get_variants(Section.PACKAGES, "django-allauth")
project.list(Section.FEATURES)
```

### TrackingOps

`TrackingOps(section)` wraps `ProjectTracking` for the installable lifecycle:

```python
TrackingOps(Section.PACKAGES).track_install(installable, variant)
TrackingOps(Section.PACKAGES).remove("my-package")
TrackingOps(Section.PACKAGES).get_variants("django-allauth")
```

Tracking data in `djdevx.toml`:

```toml
[packages.whitenoise]
installed = true
display_name = "Whitenoise"

[packages."django-allauth"]
installed = true
display_name = "Django Allauth"
variants = ["account", "mfa"]
```

### Standalone Queries

`tracking.py` also provides standalone functions that take a class reference:

```python
get_installed_names(BasePackage)        # dict of installed
get_available_names(BasePackage)        # all registered
get_installable_names(BasePackage)      # available but not installed
get_installed_variants(BasePackage, name)
get_display_name(BasePackage, name)
```

## CLI Commands

Every category exposes the same three commands:

```bash
ddx <category> add [NAME] [-p provider] [-v]
ddx <category> remove [NAME] [-p provider] [-v]
ddx <category> list
```

- `[NAME]` is optional — omit for interactive selection
- `-p / --provider` selects a variant (for types that have variants)
- `-v / --verbose` shows full pixi output

### Add Command Pattern

When `name` is `None`, the add command presents interactive selection:
- **Single-choice** (databases, caches): `prompts.select()`
- **Multi-select** (packages, features, frameworks): `prompts.checkbox()`

When `name` is provided, it installs directly. The command checks if the item
is already installed and skips with a message if so.

### Remove Command Pattern

Same interactive selection pattern. For types with variants:
- **Exclusive variants**: removes the entire item
- **Non-exclusive variants**: presents checkbox to select which variants to remove

### List Command

All categories use the shared `build_list_table()`:

```python
def list_frameworks_table() -> None:
    build_list_table(BaseFramework, "Framework")
```

Renders a Rich table with green check marks for installed items and red crosses
for not-installed items.

## Resolver — `resolver.py`

Resolves an `InstallableRef` to its concrete class by dispatching to the
correct category registry:

```python
from .types import PACKAGE, FEATURE, FRAMEWORK, DATABASE, CACHE, InstallableRef

def resolve(ref: InstallableRef) -> type:
    if ref.kind == PACKAGE:
        return get_package(ref.name)
    if ref.kind == FEATURE:
        return get_feature(ref.name)
    ...
```

Used by the orchestrator's `_auto_install_needs()` to find and install
dependencies across categories.

## Creating a New Category

To add an entirely new type of installable (e.g., "monitoring"):

1. Create the category directory with `__init__.py`, `_base.py`,
   `_registry.py`, `add.py`, `remove.py`, `list.py`
2. Define an `InstallableKind` singleton in your category (or use an existing
   one from `types.py`)
3. Implement `BaseMonitoring(Installable)` with `get_registry()` and
   `section: str = "monitoring"`
4. In `_registry.py`, create the typed registry:
   ```python
   MONITORING_REGISTRY: Registry[BaseMonitoring] = Registry(MONITORING)
   register = MONITORING_REGISTRY.register
   ```
5. Register the typer app in `djdevx/main.py`:
   ```python
   from .monitoring import app as monitoring_app
   app.add_typer(monitoring_app, name="monitoring", help="Manage monitoring tools")
   ```
6. Add a concrete installable in `monitoring/<item>/__init__.py` with `@register`

## Creating a New Installable in an Existing Category

See [Creating an Installable](creating-an-installable.md) — the shared pattern
and concepts common to all five categories. Then follow the type-specific
guide: [Add a Package](adding-a-package.md), [Add a Feature](adding-a-feature.md),
[Add a Framework](adding-a-framework.md), [Add a Database](adding-a-database.md),
or [Add a Cache](adding-a-cache.md).
