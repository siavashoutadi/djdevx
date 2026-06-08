# Managing Features

`djdevx` can add high-level features to your Django project beyond individual
packages. These features often span multiple packages, templates, and
configuration changes.

## Usage

```bash
# Install a feature
ddx backend django feature pwa --app-name myapp --port 8000

# Remove a feature
ddx backend django feature css bootstrap remove

# List installed features
ddx backend django list features

# Show available features
ddx backend django feature --help
```

## Behind the Scenes

When you install a feature, djdevx:

1. **Adds dependencies** -- Runs `uv add` for required Python packages
2. **Copies templates** -- Renders Jinja2 templates into the project
3. **Appends settings** -- Modifies `INSTALLED_APPS`, `MIDDLEWARE`, templates, etc.
4. **Tracks installation** -- Records the installation under `.djdevx/`

## Example Features

| Feature | Command | Notes |
|---------|---------|-------|
| PWA | `ddx backend django feature pwa` | Progressive Web App with manifest and service worker |
| Bootstrap | `ddx backend django feature css bootstrap` | Bootstrap 5 CSS framework |

## Finding Features

Run `ddx backend django feature --help` to see all available features.
Run `ddx backend django list features` to see which are installed in the
current project.

For complete reference including every option and parameter, see the
[Full Manual](../cli/manual.md).
