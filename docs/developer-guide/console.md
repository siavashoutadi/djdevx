# Console Utilities

djdevx provides a centralized console output system via `PrintConsole` and
styled prompt wrappers. All CLI output should go through these utilities
to maintain consistent styling.

## PrintConsole

`PrintConsole` (`djdevx/utils/console/print.py`) wraps Rich's `Console` for
styled terminal output. A singleton instance is available as `print_console`.

```python
from djdevx.utils.console.print import print_console
```

### Methods

| Method | Style | Description |
|--------|-------|-------------|
| `step(line)` | Blue checkbox ☐ | Pending step indicator |
| `step_done(line)` | Blue checked box ☑ | Completed step indicator |
| `success(line)` | Bold green | Success message |
| `error(line)` | Bold red | Error message |
| `info(line)` | Plain | Unstyled information |
| `warning(line)` | Bold yellow | Warning message |
| `ok(message)` | Green ✓ | Green checkmark with message |
| `fail(message)` | Red ✗ | Red cross with message |
| `list(items)` | Bullet points | Print a list with 🔹 bullets |
| `table(title, columns, ...)` | TableBuilder | Create a styled table. Returns a `TableBuilder` with `.add_row()` and `.render()`, or use as a context manager for auto-rendering |
| `diff(old, new)` | Side-by-side | Print a diff comparison |

### Usage Patterns

```python
from djdevx.utils.console.print import print_console

# Step-by-step progress
print_console.step("Installing package...")
print_console.ok("Installed dependency")
print_console.step_done("Package installed.")

# Status messages
print_console.success("All done!")
print_console.error("Something went wrong")
print_console.warning("This is deprecated")

# Information
print_console.info("No packages selected.")
print_console.list(["item1", "item2", "item3"])

# Tables (context manager auto-renders on exit)
columns = [
    ("Status", {"width": 8, "justify": "center", "no_wrap": True}),
    ("Name", {"style": "bold", "min_width": 16, "no_wrap": True}),
    ("Source", {"style": "dim", "overflow": "ellipsis"}),
]
with print_console.table("Secrets (dev)", columns, show_lines=False) as tbl:
    tbl.add_row("✓", "SECRET_KEY", "environment")

# Diff comparison
print_console.diff(old_content, new_content, title_old="before", title_new="after")
```

### Markup Sentinel

For intentional Rich markup strings (like styled checkmarks), use the `Markup`
class to prevent auto-escaping by `TableBuilder.add_row`:

```python
from djdevx.utils.console.print import Markup

styled = Markup("[bold green]✓[/bold green]")
with print_console.table("Title", columns) as tbl:
    tbl.add_row(styled, "plain text")  # styled not escaped
```

## Prompt Wrappers

`djdevx/utils/console/prompts.py` wraps questionary with a consistent style.

```python
from djdevx.utils.console import prompts
```

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `select(message, choices)` | `str \| None` | Single-choice selection |
| `checkbox(message, choices)` | `list[str] \| None` | Multi-select checkbox |
| `confirm(message, default)` | `bool \| None` | Yes/no confirmation |
| `text(message, default)` | `str \| None` | Text input |
| `password(message, default)` | `str \| None` | Hidden text input |

### Choice Objects

For rich choices with display titles:

```python
from djdevx.utils.console.prompts import Choice

choices = [
    Choice(title="Amazon SES", value="ses"),
    Choice(title="Brevo", value="brevo"),
]
selected = prompts.select("Which provider?", choices=choices)
```

For checkbox with pre-checked items:

```python
choices = [
    Choice(title="Account", value="account", checked=True),
    Choice(title="MFA", value="mfa", checked=False),
]
selected = prompts.checkbox("Select features:", choices=choices)
```

### Usage Patterns

```python
from djdevx.utils.console import prompts

# Single selection
name = prompts.select("Which database?", choices=["postgres", "mysql"])

# Multi-select
selected = prompts.checkbox("Select packages:", choices=["whitenoise", "cors"])

# Confirmation
if prompts.confirm("Continue?", default=True):
    ...

# Text input
api_key = prompts.text("API key:", default="")

# Password input
secret = prompts.password("Secret value:")
```

### Interactive Fallback Pattern

For commands that accept both CLI flags and interactive input, make parameters
`Optional` with `None` defaults and prompt via questionary when not provided.
Never use `typer.Option(prompt=...)` — always use the `prompts` wrappers.

```python
import typer
from typing import Optional
from typing_extensions import Annotated
from djdevx.utils.console import prompts

def my_command(
    name: Annotated[
        Optional[str], typer.Option(help="Item name")
    ] = None,
    provider: Annotated[
        Optional[str], typer.Option("--provider", "-p", help="Provider")
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose output")
    ] = False,
) -> None:
    if name is None:
        name = prompts.text("Item name")
        if name is None:
            raise typer.Abort()

    if provider is None:
        provider = prompts.select(
            "Which provider?", choices=["postgres", "mysql", "sqlite"]
        )
        if provider is None:
            raise typer.Abort()

    # ... command logic using name, provider, verbose
```

When the user runs `my-command --name foo --provider postgres`, the questionary
prompts are skipped entirely. When flags are omitted, the interactive prompts
fill in the gaps.

### Handling Ctrl+C

All prompt functions return `None` when the user presses Ctrl+C or Escape.
Always check for `None` and abort:

```python
result = prompts.text("Enter a value")
if result is None:
    raise typer.Abort()
```

### Prompt Type Guide

| Scenario | Function | Example |
|----------|----------|---------|
| Pick one from a known list | `prompts.select()` | Database provider, cache backend |
| Pick many from a known list | `prompts.checkbox()` | Packages to install, features to enable |
| Yes/no decision | `prompts.confirm()` | Initialize git? Enable debug mode? |
| Free-form string input | `prompts.text()` | Project name, description |
| Sensitive/hidden input | `prompts.password()` | API keys, tokens, secrets |

For select and checkbox, use `Choice` objects when you need display titles
different from the underlying values:

```python
from djdevx.utils.console.prompts import Choice

choices = [
    Choice(title="PostgreSQL", value="postgres"),
    Choice(title="MySQL", value="mysql"),
]
db = prompts.select("Which database?", choices=choices)
```

## Style Guidelines

- Use `step()` / `step_done()` for progress indication during install/remove
- Use `ok()` / `fail()` for final status of individual operations
- Use `success()` / `error()` for top-level completion messages
- Use `warning()` for non-fatal issues
- Use `info()` for neutral messages (selections, no-ops)
- Use `list()` for displaying multiple items
- Use `table()` with a context manager to build and render tables (auto-escapes plain strings)
- Use `diff()` when showing file changes to the user

All table row values are auto-escaped via `escape()` unless wrapped in `Markup`. Use `Markup` for intentional Rich markup strings (e.g., styled checkmarks).

## Related

- [Code Standards](code-standards.md) — Console output conventions
- [Installable System](installable-system.md) — Uses `print_console` throughout
