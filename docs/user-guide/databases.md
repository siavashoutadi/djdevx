# Database Management

`djdevx` can manage and configure databases for development with devcontainer
support. **Only one database can be installed at a time.**

Currently only PostgreSQL is supported, but more databases will be added in
the future.

## Usage

```bash
# Install a database
ddx database add postgres

# Remove a database
ddx database remove postgres

# List all databases with install status
ddx database list

# Interactive selection (omit [NAME])
ddx database add
ddx database remove
```

## Shell Autocompletion

The `[NAME]` argument supports tab completion:
- `ddx database add <TAB>` — lists available (not installed) databases
- `ddx database remove <TAB>` — lists installed databases

## Single-Instance Constraint

Only one database can be installed at a time. If a database is already
installed, attempting to add another will show an error:

```
$ ddx database add mysql
A database (postgres) is already installed.
Only one database can be installed at a time.
```

Remove the existing database first, then install the new one.

## Example

```bash
ddx database add postgres
```

## Finding More

See the [Full Manual](../cli/manual.md) for complete reference.
