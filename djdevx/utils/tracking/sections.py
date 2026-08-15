"""Section — the tracking sections of djdevx.toml."""

from enum import StrEnum


class Section(StrEnum):
    """Top-level sections in djdevx.toml used for tracking installs."""

    PACKAGES = "packages"
    FEATURES = "features"
    FRAMEWORKS = "frameworks"
    DATABASE = "database"
    CACHE = "cache"
