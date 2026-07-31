# Managing Features

`djdevx` can add high-level features to your Django project beyond individual
packages. These features often span multiple packages, templates, and
configuration changes.

## Usage

```bash
# Install a feature
ddx features add tailwind-ui

# Remove a feature
ddx features remove pwa

# List all features with install status
ddx features list

# Interactive selection (omit [NAME])
ddx features add
ddx features remove
```

## Example Features

| Feature        | Command                           | Notes                                                |
| -------------- | --------------------------------- | ---------------------------------------------------- |
| PWA            | `ddx features add pwa`            | Progressive Web App with manifest and service worker |
| Tailwind UI    | `ddx features add tailwind-ui`    | Tailwind CSS UI components                           |
| Tailwind Theme | `ddx features add tailwind-theme` | Custom tailwind theme configuration                  |

## Shell Autocompletion

The `[NAME]` argument supports tab completion:
- `ddx features add <TAB>` — lists features not yet installed
- `ddx features remove <TAB>` — lists installed features

For complete reference including every option and parameter, see the
[Full Manual](../cli/manual.md).
