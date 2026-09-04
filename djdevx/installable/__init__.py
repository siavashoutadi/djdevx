from .lifecycle import Installable
from djdevx.core.discovery import discover_and_register
from .list_table import build_list_table
from .peers import call_peer, sync_on_add, sync_on_remove
from .registry import Registry
from .models import (
    InstallParam,
    InstallableRef,
    Variant,
)

__all__ = [
    "Installable",
    "InstallParam",
    "InstallableRef",
    "Registry",
    "Variant",
    "build_list_table",
    "call_peer",
    "discover_and_register",
    "sync_on_add",
    "sync_on_remove",
]
