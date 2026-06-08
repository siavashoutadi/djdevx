# Database Management

`djdevx` can manage and configure different databases for development with
devcontainer support. Currently only PostgreSQL is supported, but more
databases will be added in the future.

## Usage

```bash
# Install PostgreSQL
ddx backend django database postgres install

# Remove PostgreSQL
ddx backend django database postgres remove

# List installed databases
ddx backend django list databases
```

## Behind the Scenes

When you install a database, djdevx:

1. **Updates settings** -- Configures `DATABASES` in Django settings
2. **Configures devcontainer** -- Adds the PostgreSQL service to
   `docker-compose.yaml`
3. **Installs dependencies** -- Adds `psycopg2-binary` to the project
4. **Tracks** -- Records the database under `.djdevx/`

## Example

```bash
ddx backend django database postgres install
```

## Finding More

Run `ddx backend django database postgres --help` for all options.
See the [Full Manual](../cli/manual.md) for complete reference.
