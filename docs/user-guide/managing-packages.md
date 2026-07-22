# Managing Packages

`djdevx` can install and configure 39+ Django packages with a single command.
Each package handles its own dependencies, settings, URL patterns, and
templates automatically.

## Usage

```bash
# Install a package
ddx backend django packages whitenoise install

# Remove a package
ddx backend django packages whitenoise remove

# List installed packages
ddx backend django list packages

# Show available packages
ddx backend django packages --help
```

## Behind the Scenes

When you run `install`, djdevx:

1. **Adds dependencies** -- Runs `pixi add` for the package's PyPI dependencies
2. **Copies templates** -- Renders Jinja2 templates into the project
3. **Appends settings** -- Adds the package to `INSTALLED_APPS`, `MIDDLEWARE`, etc.
4. **Appends URL patterns** -- Registers the package's URLs in the project
5. **Generates secrets** -- Creates any required `SecretStr` values in `.secrets/`
6. **Tracks installation** -- Records the installation under `.djdevx/`

When you run `remove`, the reverse happens: dependencies are removed via
`pixi remove`, template files are deleted, and tracking is cleaned up.

## Example Packages

| Package | Command | Notes |
|---------|---------|-------|
| whitenoise | `ddx backend django packages whitenoise install` | Static file serving, zero config |
| django-debug-toolbar | `ddx backend django packages django-debug-toolbar install` | Debug toolbar for development |
| djangorestframework | `ddx backend django packages djangorestframework install` | REST API framework |
| django-cors-headers | `ddx backend django packages django-cors-headers install` | CORS header support |

## Finding Packages

Run `ddx backend django packages --help` to see all 39+ available packages.
Run `ddx backend django list packages` to see which are installed in the
current project.

For complete reference including every option and parameter, see the
[Full Manual](../cli/manual.md).
