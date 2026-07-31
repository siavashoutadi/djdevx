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
| `table(table)` | Rich Table | Render a Rich `Table` object |
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

# Tables (requires Rich Table)
from rich.table import Table
table = Table(title="Packages")
table.add_column("Name")
table.add_row("whitenoise")
print_console.table(table)

# Diff comparison
print_console.diff(old_content, new_content, title_old="before", title_new="after")
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

## Style Guidelines

- Use `step()` / `step_done()` for progress indication during install/remove
- Use `ok()` / `fail()` for final status of individual operations
- Use `success()` / `error()` for top-level completion messages
- Use `warning()` for non-fatal issues
- Use `info()` for neutral messages (selections, no-ops)
- Use `list()` for displaying multiple items
- Use `table()` for structured data (package lists, status tables)
- Use `diff()` when showing file changes to the user

All methods auto-escape Rich markup in user-provided strings via `escape()`.

## Related

- [Code Standards](code-standards.md) — Console output conventions
- [Installable System](installable-system.md) — Uses `print_console` throughout
