"""Auto-discover and import modules to trigger @register decorators."""

import importlib
import pkgutil
from collections.abc import Sequence


def discover_and_register(search_path: Sequence[str], package_name: str) -> None:
    """Import every module under *search_path* to trigger @register decorators.

    Internal modules (leading ``_``), command modules (``add``, ``remove``,
    ``list``), and the ``types`` module are skipped automatically.
    Import errors are silenced so that an optional dependency being missing
    does not crash the CLI.
    """
    _skip = {"add", "remove", "list", "types"}
    for _, name, _ispkg in pkgutil.iter_modules(search_path, package_name + "."):
        short = name.rsplit(".", 1)[-1]
        if short.startswith("_") or short in _skip:
            continue
        try:
            importlib.import_module(name)
        except ImportError:
            pass
