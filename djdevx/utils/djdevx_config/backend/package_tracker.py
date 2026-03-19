"""Package tracking for djdevx - records installed packages under .djdevx/."""

import shutil
from pathlib import Path

import tomlkit

from ..project import ProjectConfig


class PackageTracker(ProjectConfig):
    """
    Tracks installed packages by maintaining config.toml files under
    .djdevx/backend/django/packages/<template_path>/.

    Installing a package creates its folder + config.toml.
    Removing a package deletes the entire folder.
    Checking if installed uses Path.exists() on the folder.
    """

    @property
    def _packages_root(self) -> Path:
        """Root path for package tracking records."""
        return self.djdevx_root / "backend" / "django" / "packages"

    def _package_dir(self, template_path: str) -> Path:
        """Directory for a specific package's tracking record."""
        return self._packages_root / template_path

    def _config_path(self, template_path: str) -> Path:
        """Path to the config.toml for a given package."""
        return self._package_dir(template_path) / "config.toml"

    def _load_or_create_doc(self, template_path: str) -> tomlkit.TOMLDocument:
        """Load existing config.toml or return an empty document."""
        config = self._config_path(template_path)
        if config.exists():
            return tomlkit.loads(config.read_text())
        return tomlkit.document()

    def _save_doc(self, template_path: str, doc: tomlkit.TOMLDocument) -> None:
        """Ensure the package directory exists and write the document."""
        self._package_dir(template_path).mkdir(parents=True, exist_ok=True)
        self._config_path(template_path).write_text(tomlkit.dumps(doc))

    def write_package_config(self, template_path: str, name: str) -> None:
        """
        Write or update only the [package] section of the config.toml.
        Existing [env] entries are preserved.

        Args:
            template_path: Relative path key (e.g. "whitenoise" or "django_anymail/brevo")
            name: Package display name
        """
        doc = self._load_or_create_doc(template_path)

        package_table = tomlkit.table()
        package_table.add("name", name)
        if "package" in doc:
            doc["package"] = package_table
        else:
            doc.add("package", package_table)

        self._save_doc(template_path, doc)

    def write_env_entries(
        self, template_path: str, env_entries: dict[str, dict[str, str]]
    ) -> None:
        """
        Write or replace the [env] section of the config.toml.
        Existing [package] data is preserved.

        Args:
            template_path: Relative path key (e.g. "whitenoise" or "django_anymail/brevo")
            env_entries: Mapping of env var key → dict with ``type`` and optional ``value``.
                         Secret values should never be passed.
        """
        doc = self._load_or_create_doc(template_path)

        env_table = tomlkit.table(is_super_table=True)
        for key, entry_data in env_entries.items():
            entry = tomlkit.table()
            entry.add("type", entry_data["type"])
            if "value" in entry_data:
                entry.add("value", entry_data["value"])
            env_table.add(key, entry)

        if "env" in doc:
            doc["env"] = env_table
        else:
            doc.add("env", env_table)

        self._save_doc(template_path, doc)

    def read_package_config(self, template_path: str) -> tomlkit.TOMLDocument:
        """
        Read and parse the config.toml for the given package.

        Args:
            template_path: Relative path key (e.g. "whitenoise")

        Returns:
            Parsed TOMLDocument for the package config.
        """
        return tomlkit.loads(self._config_path(template_path).read_text())

    def remove_env_entries(self, template_path: str) -> None:
        """
        Remove the [env] section from the config.toml, leaving [package] intact.
        No-op if the file or section does not exist.

        Args:
            template_path: Relative path key (e.g. "whitenoise")
        """
        config = self._config_path(template_path)
        if not config.exists():
            return
        doc = tomlkit.loads(config.read_text())
        if "env" in doc:
            del doc["env"]
            config.write_text(tomlkit.dumps(doc))

    def remove_package_config(self, template_path: str) -> None:
        """
        Remove the entire tracking folder for the given package.

        Args:
            template_path: Relative path key (e.g. "whitenoise")
        """
        shutil.rmtree(self._package_dir(template_path), ignore_errors=True)

    def is_installed(self, template_path: str) -> bool:
        """
        Check if the package tracking folder exists.

        Args:
            template_path: Relative path key (e.g. "whitenoise")

        Returns:
            True if the package tracking folder exists, False otherwise.
        """
        return self._package_dir(template_path).exists()
