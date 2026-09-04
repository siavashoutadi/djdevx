"""Database registry — DATABASE_REGISTRY dict and register decorator."""

from ...utils.installable.registry import Registry
from ...utils.installable.types import DATABASE
from ._base import BaseDatabase

DATABASE_REGISTRY: Registry[BaseDatabase] = Registry(DATABASE)
register = DATABASE_REGISTRY.register
get_database = DATABASE_REGISTRY.get
list_databases = DATABASE_REGISTRY.names
