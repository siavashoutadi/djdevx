"""Feature tracking for djdevx - records installed features under .djdevx/."""

import shutil
from pathlib import Path

import tomlkit

from ..project import ProjectConfig


class FeatureTracker(ProjectConfig):
    """
    Tracks installed features by maintaining config.toml files under
    .djdevx/backend/django/features/<feature_name>/.

    Installing a feature creates its folder + config.toml.
    Removing a feature deletes the entire folder.
    Checking if installed uses Path.exists() on the folder.
    """

    @property
    def _features_root(self) -> Path:
        """Root path for feature tracking records."""
        return self.djdevx_root / "backend" / "django" / "features"

    def _feature_dir(self, feature_name: str) -> Path:
        """Directory for a specific feature's tracking record."""
        return self._features_root / feature_name

    def _config_path(self, feature_name: str) -> Path:
        """Path to the config.toml for a given feature."""
        return self._feature_dir(feature_name) / "config.toml"

    def write_feature_config(self, feature_name: str, name: str) -> None:
        """
        Write or update the [feature] section of the config.toml.

        Args:
            feature_name: Relative path key (e.g. "tailwind_theme" or "css/bootstrap")
            name: Feature display name
        """
        feature_dir = self._feature_dir(feature_name)
        config = self._config_path(feature_name)

        if config.exists():
            doc = tomlkit.loads(config.read_text())
        else:
            doc = tomlkit.document()

        feature_table = tomlkit.table()
        feature_table.add("name", name)
        if "feature" in doc:
            doc["feature"] = feature_table
        else:
            doc.add("feature", feature_table)

        feature_dir.mkdir(parents=True, exist_ok=True)
        config.write_text(tomlkit.dumps(doc))

    def read_feature_config(self, feature_name: str) -> tomlkit.TOMLDocument:
        """
        Read and parse the config.toml for the given feature.

        Args:
            feature_name: Relative path key (e.g. "tailwind_theme")

        Returns:
            Parsed TOMLDocument for the feature config.
        """
        return tomlkit.loads(self._config_path(feature_name).read_text())

    def remove_feature_config(self, feature_name: str) -> None:
        """
        Remove the entire tracking folder for the given feature.

        Args:
            feature_name: Relative path key (e.g. "tailwind_theme")
        """
        shutil.rmtree(self._feature_dir(feature_name), ignore_errors=True)

    def is_installed(self, feature_name: str) -> bool:
        """
        Check if the feature tracking folder exists.

        Args:
            feature_name: Relative path key (e.g. "tailwind_theme")

        Returns:
            True if the feature tracking folder exists, False otherwise.
        """
        return self._feature_dir(feature_name).exists()
