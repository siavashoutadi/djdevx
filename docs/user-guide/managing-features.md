# Managing Features

`djdevx` can add high-level features to your Django project beyond individual
packages. These features often span multiple packages, templates, and
configuration changes.

## Usage

```bash
# Install a feature
ddx features add pwa

# Remove a feature
ddx features remove pwa

# List all features with install status
ddx features list

# Interactive selection (omit [NAME])
ddx features add
ddx features remove
```

## Available Features

| Feature | Command                        | Notes                                                |
| ------- | ------------------------------ | ---------------------------------------------------- |
| PWA     | `ddx features add pwa`         | Progressive Web App with manifest and service worker |
| Sentry  | `ddx features add sentry`      | Error monitoring, tracing, and log shipping          |

See [Sentry](sentry.md) for the Sentry feature's setup, configuration, and
troubleshooting.

## Secrets a feature requires

Some features need a value you must obtain from a third party — the Sentry DSN
is the example. Such a value is declared as a required secret with no default,
so the feature never writes a placeholder that would silently drop data.

Installing it does **not** prompt: the feature prints the command to run
instead.

```bash
ddx features add sentry
# ...
#   ⚠ Sentry DSN is required but was not configured
#   ddx settings secrets init dev      (local development)
```

Until you run that command, Django will not import. See
[Managing Settings](managing-settings.md) for how secrets work.

## Shell Autocompletion

The `[NAME]` argument supports tab completion:
- `ddx features add <TAB>` — lists features not yet installed
- `ddx features remove <TAB>` — lists installed features

For complete reference including every option and parameter, see the
[Full Manual](../cli/manual.md).
