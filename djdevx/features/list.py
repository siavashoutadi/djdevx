"""Feature list command — shows all available features in a table."""

from ._base import BaseFeature
from ..utils.installable.list_table import build_list_table


def list_features_table() -> None:
    """List all available features with install status in a table."""
    build_list_table(BaseFeature, "Feature")
