"""Cache tracking for djdevx - records installed caches under .djdevx/."""

import shutil
from pathlib import Path

import tomlkit

from ..project import ProjectConfig


class CacheTracker(ProjectConfig):
    """
    Tracks installed caches by maintaining config.toml files under
    .djdevx/backend/django/cache/<cache_key>/.

    Installing a cache creates its folder + config.toml.
    Removing a cache deletes the entire folder.
    Checking if installed uses Path.exists() on the folder.
    """

    @property
    def _cache_root(self) -> Path:
        """Root path for cache tracking records."""
        return self.djdevx_root / "backend" / "django" / "cache"

    def _cache_dir(self, cache_key: str) -> Path:
        """Directory for a specific cache's tracking record."""
        return self._cache_root / cache_key

    def _config_path(self, cache_key: str) -> Path:
        """Path to the config.toml for a given cache."""
        return self._cache_dir(cache_key) / "config.toml"

    def _load_or_create_doc(self, cache_key: str) -> tomlkit.TOMLDocument:
        """Load existing config.toml or return an empty document."""
        config = self._config_path(cache_key)
        if config.exists():
            return tomlkit.loads(config.read_text())
        return tomlkit.document()

    def _save_doc(self, cache_key: str, doc: tomlkit.TOMLDocument) -> None:
        """Ensure the cache directory exists and write the document."""
        self._cache_dir(cache_key).mkdir(parents=True, exist_ok=True)
        self._config_path(cache_key).write_text(tomlkit.dumps(doc))

    def write_cache_config(self, cache_key: str, name: str) -> None:
        """
        Write or update the [cache] section of the config.toml.
        Existing [env] entries are preserved.

        Args:
            cache_key: Short identifier for the cache (e.g. "redis")
            name: Cache display name (e.g. "redis")
        """
        doc = self._load_or_create_doc(cache_key)

        cache_table = tomlkit.table()
        cache_table.add("name", name)
        if "cache" in doc:
            doc["cache"] = cache_table
        else:
            doc.add("cache", cache_table)

        self._save_doc(cache_key, doc)

    def read_cache_config(self, cache_key: str) -> tomlkit.TOMLDocument:
        """
        Read and parse the config.toml for the given cache.

        Args:
            cache_key: Short identifier for the cache (e.g. "redis")

        Returns:
            Parsed TOMLDocument for the cache config.
        """
        return tomlkit.loads(self._config_path(cache_key).read_text())

    def remove_cache_config(self, cache_key: str) -> None:
        """
        Remove the entire tracking folder for the given cache.
        No-op if the folder does not exist.

        Args:
            cache_key: Short identifier for the cache (e.g. "redis")
        """
        shutil.rmtree(self._cache_dir(cache_key), ignore_errors=True)

    def is_installed(self, cache_key: str) -> bool:
        """
        Check if the cache tracking folder exists.

        Args:
            cache_key: Short identifier for the cache (e.g. "redis")

        Returns:
            True if the cache tracking folder exists, False otherwise.
        """
        return self._cache_dir(cache_key).exists()
