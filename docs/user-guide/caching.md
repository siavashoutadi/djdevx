# Cache Management

`djdevx` can manage and configure different cache backends for development
with devcontainer support. Currently only Redis is supported, but more cache
backends will be added in the future.

## Usage

```bash
# Install Redis cache
ddx backend django cache redis install

# Remove Redis cache
ddx backend django cache redis remove

# List installed caches
ddx backend django list caches
```

## Behind the Scenes

When you install a cache, djdevx:

1. **Configures settings** -- Adds `CACHES` backend configuration
2. **Configures devcontainer** -- Adds the Redis service to
   `docker-compose.yaml`
3. **Installs dependencies** -- Adds `django-redis` to the project
4. **Tracks** -- Records the cache under `.djdevx/`

## Example

```bash
ddx backend django cache redis install
```

## Finding More

Run `ddx backend django cache redis --help` for all options.
See the [Full Manual](../cli/manual.md) for complete reference.
