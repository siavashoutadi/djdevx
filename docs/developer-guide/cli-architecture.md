# CLI Overview

`djdevx` uses [Typer](https://typer.tiangolo.com/) for its CLI. Commands are
organized as nested sub-apps with `no_args_is_help=True` on all levels.

## Entry Points

- `djdevx` -- full command name
- `ddx` -- shorthand alias

Both point to `djdevx.main:app`.

## Command Tree

```
ddx
├── version                          # Show version
├── requirement                      # Check system requirements
├── new
│   └── backend
│       └── django                   # Scaffold new Django project
│           [--project-name]         #   Default: my-project
│           [--project-description]  #   Default: My project is awesome
│           [--project-directory]    #   Default: .
└── backend
    └── django
        ├── packages                 # Django package management
        │   ├── <name> install       #   Install a package
        │   ├── <name> remove        #   Remove a package
        │   └── <name> configure     #   Configure an installed package
        ├── feature                  # Feature management
        │   ├── pwa                  #   Add PWA support
        │   └── css                  #   Add CSS framework
        ├── create
        │   └── app                  # Scaffold a new Django app
        ├── database                 # PostgreSQL management
        │   ├── create               #   Create a database
        │   ├── remove               #   Remove a database
        │   └── list                 #   List databases
        ├── cache                    # Redis management
        │   ├── create               #   Create a cache
        │   ├── remove               #   Remove a cache
        │   └── list                 #   List caches
        ├── settings                 # Configuration
        │   ├── secret               #   Manage secrets
        │   ├── config               #   Manage config vars
        │   └── list                 #   List settings
        └── list                     # Show installed state
            ├── packages             #   Installed packages
            ├── features             #   Installed features
            ├── databases            #   Managed databases
            └── caches               #   Managed caches
```

## CLI Conventions

- **`no_args_is_help=True`** — Every `typer.Typer()` instance uses this so
  running a command without arguments shows its help.

- **Options only, no Arguments** — All CLI parameters use
  `Annotated[type, typer.Option(...)]`. `typer.Argument()` is never used.

- **Prompt pattern** — If a value is missing and has no sensible default, the
  developer decides whether to prompt the user. Two approaches:
  - `typer.Option(prompt="...")` — prompts automatically when the option is
    omitted on the command line
  - `typer.prompt(...)` — inline function for conditional prompts (e.g., only
    when a gating flag is set)

- **Folder-per-command-group** — Each group of related commands lives in its
  own directory with an `__init__.py` that creates the sub-typer and registers
  command modules:

  ```
  feature/
  ├── __init__.py          # typer.Typer() + add_typer(...)
  ├── pwa.py
  ├── tailwind_theme.py
  └── css/
      ├── __init__.py
      ├── bootstrap.py
      └── frankenui.py
  ```

- **Validation via callbacks** — Input validation uses `callback=func` on
  `typer.Option()`. The callback raises `typer.BadParameter(...)` on invalid
  input and returns the (possibly transformed) valid value.

- **Error exits** — Commands abort with `typer.Exit(code=1)` on failures
  (missing dependencies, invalid state). Early success exits use
  `typer.Exit(0)` (e.g., empty list results).

## Adding New Sub-commands

New sub-commands follow this pattern:

```python
# djdevx/backend/django/new_feature/__init__.py
import typer

app = typer.Typer(no_args_is_help=True)

@app.command()
def my_command():
    """Do something useful."""
    ...
```

Then register in the parent app:
```python
from .new_feature import app as new_feature_app
parent_app.add_typer(new_feature_app, name="new-feature")
```

## References

- [CLI Full Manual](../cli/manual.md) -- Full command reference
