# Cache Management

`djdevx` can manage and configure cache backends for development with
devcontainer support. **Only one cache can be installed at a time.**

Currently only Redis is supported, but more cache backends will be added in
the future.

## Usage

```bash
# Install a cache
ddx cache add redis

# Remove a cache
ddx cache remove redis

# List all caches with install status
ddx cache list

# Interactive selection (omit [NAME])
ddx cache add
ddx cache remove
```

## Shell Autocompletion

The `[NAME]` argument supports tab completion:
- `ddx cache add <TAB>` — lists available (not installed) caches
- `ddx cache remove <TAB>` — lists installed caches

## Single-Instance Constraint

Only one cache can be installed at a time. If a cache is already installed,
attempting to add another will show an error:

```
$ ddx cache add memcached
A cache (redis) is already installed.
Only one cache can be installed at a time.
```

Remove the existing cache first, then install the new one.

## Example

```bash
ddx cache add redis
```

## Finding More

See the [Full Manual](../cli/manual.md) for complete reference.
