"""Server extensions — feature-provided modules loaded only in server processes.

Extensions live in this package as plain modules (e.g. dropped in by djdevx
features or packages via their templates). ``load()`` is called from the
project's ASGI and WSGI entrypoints after the Django application is built,
so extension code never runs in management commands or tests.

An extension may define a module-level ``load(application)`` hook; it is
called after import with the application instance built by the entrypoint.
An extension that needs to wrap the application (e.g. Channels' protocol
router) rebinds ``applications.asgi.application`` inside its hook; hook
return values are ignored.

Module names starting with ``_`` are skipped. Import or hook errors are
logged and do not stop the server from booting.
"""

import importlib
import logging
import pkgutil
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

_loaded = False


def load(application: Callable[..., Any]) -> None:
    """Import every extension module and call its ``load()`` hook, once."""
    global _loaded
    if _loaded:
        return
    _loaded = True

    for module_info in sorted(
        pkgutil.iter_modules(__path__), key=lambda info: info.name
    ):
        if module_info.name.startswith("_"):
            continue
        module_name = f"{__name__}.{module_info.name}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            logger.exception("Server extension %r failed to import", module_name)
            continue
        hook = getattr(module, "load", None)
        if callable(hook):
            try:
                hook(application)
            except Exception:
                logger.exception("Server extension %r failed to load", module_name)
