import warnings

from .project_manager import DjangoProjectManager


def get_dependencies(group: str = "") -> list[str]:
    warnings.warn(
        "get_dependencies is deprecated. Use DjangoProjectManager().get_dependencies() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    pm = DjangoProjectManager()
    return pm.get_dependencies(group)


def has_dependency(dependency_name: str, group: str = "") -> bool:
    warnings.warn(
        "has_dependency is deprecated. Use DjangoProjectManager().has_dependency() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    pm = DjangoProjectManager()
    return pm.has_dependency(dependency_name, group)
