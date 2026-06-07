"""Database tracking for djdevx - records installed databases under .djdevx/."""

import shutil
from pathlib import Path

import tomlkit

from ..project import ProjectConfig


class DatabaseTracker(ProjectConfig):
    """
    Tracks installed databases by maintaining config.toml files under
    .djdevx/backend/django/database/<db_key>/.

    Installing a database creates its folder + config.toml.
    Removing a database deletes the entire folder.
    Checking if installed uses Path.exists() on the folder.
    """

    @property
    def _database_root(self) -> Path:
        """Root path for database tracking records."""
        return self.djdevx_root / "backend" / "django" / "database"

    def _database_dir(self, db_key: str) -> Path:
        """Directory for a specific database's tracking record."""
        return self._database_root / db_key

    def _config_path(self, db_key: str) -> Path:
        """Path to the config.toml for a given database."""
        return self._database_dir(db_key) / "config.toml"

    def _load_or_create_doc(self, db_key: str) -> tomlkit.TOMLDocument:
        """Load existing config.toml or return an empty document."""
        config = self._config_path(db_key)
        if config.exists():
            return tomlkit.loads(config.read_text())
        return tomlkit.document()

    def _save_doc(self, db_key: str, doc: tomlkit.TOMLDocument) -> None:
        """Ensure the database directory exists and write the document."""
        self._database_dir(db_key).mkdir(parents=True, exist_ok=True)
        self._config_path(db_key).write_text(tomlkit.dumps(doc))

    def write_database_config(self, db_key: str, name: str) -> None:
        """
        Write or update the [database] section of the config.toml.
        Existing [env] entries are preserved.

        Args:
            db_key: Short identifier for the database (e.g. "postgres")
            name: Database display name (e.g. "PostgreSQL")
        """
        doc = self._load_or_create_doc(db_key)

        database_table = tomlkit.table()
        database_table.add("name", name)
        if "database" in doc:
            doc["database"] = database_table
        else:
            doc.add("database", database_table)

        self._save_doc(db_key, doc)

    def read_database_config(self, db_key: str) -> tomlkit.TOMLDocument:
        """
        Read and parse the config.toml for the given database.

        Args:
            db_key: Short identifier for the database (e.g. "postgres")

        Returns:
            Parsed TOMLDocument for the database config.
        """
        return tomlkit.loads(self._config_path(db_key).read_text())

    def remove_database_config(self, db_key: str) -> None:
        """
        Remove the entire tracking folder for the given database.
        No-op if the folder does not exist.

        Args:
            db_key: Short identifier for the database (e.g. "postgres")
        """
        shutil.rmtree(self._database_dir(db_key), ignore_errors=True)

    def is_installed(self, db_key: str) -> bool:
        """
        Check if the database tracking folder exists.

        Args:
            db_key: Short identifier for the database (e.g. "postgres")

        Returns:
            True if the database tracking folder exists, False otherwise.
        """
        return self._database_dir(db_key).exists()
