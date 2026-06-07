"""
Lightweight registries for database and cache plugins.

These are separate from the main PACKAGE_REGISTRY because database and cache
installers don't currently extend BasePackage. They only need to expose
secret_generators for the SettingCollector to build its generators index.

Keys match the DatabaseTracker / CacheTracker db_key / cache_key values.
"""

from typing import Callable


class _DatabasePlugin:
    """Minimal registry entry for a database backend."""

    secret_generators: dict[str, Callable[[], str]] = {}


class _CachePlugin:
    """Minimal registry entry for a cache backend."""

    secret_generators: dict[str, Callable[[], str]] = {}


class PostgresPlugin(_DatabasePlugin):
    """PostgreSQL — password has a dev default, no auto-generator needed."""

    secret_generators: dict[str, Callable[[], str]] = {}


class RedisPlugin(_CachePlugin):
    """Redis — password has a dev default, no auto-generator needed."""

    secret_generators: dict[str, Callable[[], str]] = {}


# Maps DatabaseTracker db_key → plugin class
DATABASE_REGISTRY: dict[str, type[_DatabasePlugin]] = {
    "postgres": PostgresPlugin,
}

# Maps CacheTracker cache_key → plugin class
CACHE_REGISTRY: dict[str, type[_CachePlugin]] = {
    "redis": RedisPlugin,
}
