---
name: Typer CLI Writer
description: Guide for writing new Typer CLI commands in djdevx
---

# Adding new cli command to djdevx

This skill helps you add new typer command and subcommands to djdevx.

## When to use this skill

Use this skill when you need to:
- Create a new typer command to djdevx

## Command Structure Basics

djdevx organizes CLI commands in a nested hierarchy using Typer. The key concepts are:

- **Command**: A function decorated with `@app.command()` that executes an action
- **App Instance**: Each module creates `app = typer.Typer()` to define commands
- **Aggregation**: Parent `__init__.py` files use `app.add_typer()` to register subcommands, building the command tree

Example hierarchy:
```
djdevx
├── version (simple command)
├── backend (subcommand group)
│   └── django (subcommand group)
│       ├── packages (subcommand group with 30+ package commands)
│       └── feature (subcommand group with feature commands)
```

## Creating a Simple Command

A simple command is a standalone function registered in a parent module:

**File: `djdevx/backend/django/packages/django_debug_toolbar.py`**
```python
import typer
from ....utils.print_console import console

app = typer.Typer(no_args_is_help=True)

@app.command()
def install():
    """Install and configure django-debug-toolbar"""
    console.step("Installing django-debug-toolbar...")
    # Implementation here
    console.success("django-debug-toolbar installed successfully.")
```

**Register in parent: `djdevx/backend/django/packages/__init__.py`**
```python
from .django_debug_toolbar import app as debug_toolbar

app = typer.Typer(no_args_is_help=True)
app.add_typer(debug_toolbar, name="django-debug-toolbar")
```

## Creating a Subcommand Group

A subcommand group aggregates multiple related commands:

**Step 1: Create individual command modules**
```python
# File: djdevx/backend/django/packages/channels.py
import typer
from ....utils.print_console import console

app = typer.Typer(no_args_is_help=True)

@app.command()
def install():
    """Install channels"""
    console.step("Installing channels...")
    # Implementation

@app.command()
def remove():
    """Remove channels"""
    console.step("Removing channels...")
    # Implementation
```

**Step 2: Aggregate in parent `__init__.py`**
```python
# File: djdevx/backend/django/packages/__init__.py
from .channels import app as channels
from .django_extensions import app as extensions
# ... import more packages

app = typer.Typer(no_args_is_help=True)
app.add_typer(channels, name="channels")
app.add_typer(extensions, name="django-extensions")
# ... register more packages
```

**Step 3: Register in grandparent module**
```python
# File: djdevx/backend/django/__init__.py
from .packages import app as packages

app = typer.Typer(no_args_is_help=True)
app.add_typer(packages, name="packages", help="Install and configure packages")
```

## Investigate the Codebase

Before implementing your command, study the existing code to understand patterns and conventions:

1. **Review [`djdevx/backend/django/packages/`](djdevx/backend/django/packages)** – Understand how package commands are structured, how `typer.Typer()` is used, how commands are aggregated in `__init__.py`, and how utilities like `PrintConsole` and `DjangoProjectManager` are used.

2. **Review [`djdevx/backend/django/feature/`](djdevx/backend/django/feature)** – See how commands with parameters and user input prompts are implemented, and how `typer.Option()` is used for interactive prompts.

3. **Review [`djdevx/backend/django/create/`](djdevx/backend/django/create)** – Understand how create commands handle template copying and context passing with Jinja2 templates.

4. **Notice the patterns** – How are imports organized? How is `PrintConsole` used for output? How do commands use `DjangoProjectManager` and `UvRunner`? How are templates stored and copied?

## Important Conventions

- **Always sort commands alphabetically** – When registering multiple subcommands in `__init__.py`, ensure they are sorted alphabetically by name for consistency and maintainability.
