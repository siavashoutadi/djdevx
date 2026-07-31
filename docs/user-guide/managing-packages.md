# Managing Packages

`djdevx` can install and configure 39+ Django packages with a single command.
Each package handles its own dependencies, settings, URL patterns, and
templates automatically.

## Usage

```bash
# Install a package
ddx packages add whitenoise

# Install with a specific variant/provider
ddx packages add django-storages --provider s3

# Remove a package
ddx packages remove whitenoise

# List all packages with install status
ddx packages list

# Interactive selection (omit [NAME])
ddx packages add
ddx packages remove
```

## Example Packages

| Package | Command | Notes |
|---------|---------|-------|
| whitenoise | `ddx packages add whitenoise` | Static file serving, zero config |
| django-debug-toolbar | `ddx packages add django-debug-toolbar` | Debug toolbar for development |
| djangorestframework | `ddx packages add djangorestframework` | REST API framework |
| django-cors-headers | `ddx packages add django-cors-headers` | CORS header support |

## Shell Autocompletion

The `[NAME]` argument supports tab completion:
- `ddx packages add <TAB>` — lists packages not yet installed
- `ddx packages remove <TAB>` — lists installed packages

For complete reference including every option and parameter, see the
[Full Manual](../cli/manual.md).
