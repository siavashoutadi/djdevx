# CLI Overview

`djdevx` uses [Typer](https://typer.tiangolo.com/) for its CLI. Commands are
organized as nested sub-apps with `no_args_is_help=True` on all levels.

## Entry Points

- `djdevx` — full command name
- `ddx` — shorthand alias

Both point to `djdevx.main:app`.

## Command Tree

```
ddx
├── version                                      # Show version
├── requirement verify                           # Check system requirements
├── new                                          # Create new Django project
│     [--project-name] [--project-description]
│     [--project-directory] [--python-version]
│     [--git-init / --no-git-init] [-v]
├── packages
│   ├── add [NAME] [-p provider] [-v]           # Install a package
│   ├── remove [NAME] [-p provider] [-v]        # Remove a package
│   └── list                                     # List packages (check/cross table)
├── frameworks
│   ├── add [NAME] [-v]                          # Add a CSS/JS framework
│   ├── remove [NAME] [-v]                       # Remove a framework
│   └── list                                     # List frameworks
├── features
│   ├── add [NAME] [-p provider] [-v]           # Install a feature
│   ├── remove [NAME] [-p provider] [-v]        # Remove a feature
│   └── list                                     # List features
├── create app                                   # Scaffold new Django app
├── database
│   ├── add [NAME] [-v]                          # Add a database (single only)
│   ├── remove [NAME] [-v]                       # Remove a database
│   └── list                                     # List databases
├── cache
│   ├── add [NAME] [-v]                          # Add a cache (single only)
│   ├── remove [NAME] [-v]                       # Remove a cache
│   └── list                                     # List caches
├── settings
│   ├── secrets {init,list,verify} [ENV]
│   └── configs {init,list,verify} [ENV]
└── deployment
    └── docker-compose {generate,verify}
```

## CLI Conventions

- **`no_args_is_help=True`** — Every `typer.Typer()` instance uses this so
  running a command without arguments shows its help.

- **Positional Arguments with Autocompletion** — Installable categories
  (`packages`, `features`, `frameworks`, `database`, `cache`) use
  `typer.Argument()` with `autocompletion=` for their `[NAME]` parameter.
  This gives shell tab-completion for available/installed items.

- **Interactive fallback** — If `[NAME]` is omitted, the command prompts
  interactively using questionary checkboxes or selects.

- **Autocomplete callbacks** — Each category's `add.py` and `remove.py` define
  autocomplete functions that delegate to the `Installable` class methods:

  ```python
  def _autocomplete_feature(incomplete: str) -> list[str]:
      return BaseFeature.autocomplete_installable(incomplete)
  ```

- **Shared list command** — All five categories use the same
  `build_list_table(cls, label)` function from
  `utils/installable/list_table.py`. Each `list.py` is a one-liner:

  ```python
  def list_features_table():
      build_list_table(BaseFeature, "Feature")
  ```

- **Discovery via discover_and_register** — Each category's `__init__.py` uses
  `discover_and_register()` to find all concrete installable modules and
  register their CLI subcommands:

  ```python
  app = typer.Typer(no_args_is_help=True)

  def _discover():
      for installable in discover_and_register(BasePackage):
          ...
      app.command(name="add")(add)
      app.command(name="remove")(remove)
      app.command(name="list")(list_)

  _discover()
  ```

- **Folder-per-command-group** — Each category lives in its own directory:

  ```
  features/
  ├── __init__.py       # typer.Typer() + discovery + command registration
  ├── _base.py           # BaseFeature(Installable)
  ├── _registry.py       # FEATURE_REGISTRY + @register
  ├── add.py             # add() command
  ├── remove.py          # remove() command
  ├── list.py            # list table
  ├── pwa/
  │   └── __init__.py    # @register PWAFeature(BaseFeature)
  ```

- **Validation via callbacks** — Input validation uses `callback=func` on
  `typer.Option()`. The callback raises `typer.BadParameter(...)` on invalid
  input and returns the (possibly transformed) valid value.

- **Error exits** — Commands abort with `typer.Exit(code=1)` on failures
  (missing dependencies, invalid state). Early success exits use
  `typer.Exit(0)` (e.g., empty list results).

## Installable Category Pattern

All five installable categories follow the same architectural pattern.
See [Installable System](installable-system.md) for the full reference.

The pattern in each `__init__.py`:

```python
app = typer.Typer(no_args_is_help=True)

from .add import add as _add
from .remove import remove as _remove
from .list import list_X_table as _list

def _discover():
    discover_and_register(BasePackage)

_discover()

app.command(name="add")(_add)
app.command(name="remove")(_remove)
app.command(name="list")(_list)
```

## Adding a New Category

To add a new installable category (e.g., "monitoring"):

1. Create the directory with the standard files:
   ```
   monitoring/
   ├── __init__.py       # typer app + auto-discovery
   ├── _base.py           # BaseMonitoring(Installable)
   ├── _registry.py       # MONITORING_REGISTRY
   ├── add.py             # add() command
   ├── remove.py          # remove() command
   └── list.py            # list table
   ```

2. Create a tracking class in `utils/tracking/`:
   ```python
   class MonitoringTracking(SectionTracking):
       def __init__(self, project_root=None):
           super().__init__("monitoring", project_root)
   ```

3. Implement `get_registry()` and `get_tracking_cls()` in `_base.py`.

4. Register in `djdevx/main.py`:
   ```python
   from .monitoring import app as monitoring_app
   app.add_typer(monitoring_app, name="monitoring", help="Manage monitoring tools")
   ```

## References

- [Installable System](installable-system.md) — Full architecture reference
- [Creating an Installable](creating-an-installable.md) — Common concepts and how-to guides with examples
- [CLI Full Manual](../cli/manual.md) — Auto-generated command reference
