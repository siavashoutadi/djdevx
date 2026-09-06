# Extensions Architecture

Server extensions are the plugin mechanism for behavior that must run **only
in real server processes** — tracing setup, ASGI application wrapping, warm-up
tasks. Unlike `settings/` includes (which execute in *every* Python process
that loads the project, including `manage.py` commands and tests), extension
modules are loaded exclusively from the project's `applications/asgi.py` and
`applications/wsgi.py` entrypoints.

This is how the otel feature activates instrumentation and how the channels
package wraps the ASGI application with its protocol router.

## Layout

```
applications/
├── asgi.py          ← base scaffold; builds app, then calls extensions.load(application)
├── wsgi.py          ← base scaffold; builds app, then calls extensions.load(application)
└── extensions/
    ├── __init__.py  ← base scaffold; the loader (pkgutil discovery)
    ├── otel.py      ← shipped by the otel feature
    └── channels.py  ← shipped by the channels package
```

The base scaffold owns `applications/__init__.py` and
`applications/extensions/__init__.py` (the loader). Features and packages
ship **only their own module** into `applications/extensions/` via their
template directory — they never overwrite scaffold files, and uninstalling
simply deletes the module (handled by the standard template-output cleanup).

## The loader

`applications/extensions/__init__.py` exposes one function:

```python
def load(application) -> None:
    """Import every extension module and call its load(application) hook, once."""
```

Semantics:

- **Called once per process.** The entrypoints invoke it after
  `get_asgi_application()` / `get_wsgi_application()`, so Django is fully
  set up (`django.setup()` has run, apps are populated, logging is
  configured). The entrypoint's application instance is passed to every
  hook.
- **Both entrypoints call it.** WSGI servers, ASGI servers, uvicorn, daphne,
  and `manage.py runserver` all trigger it; management commands never do.
- **Modules run in sorted name order** for deterministic behavior; names
  starting with `_` are skipped (useful to park a disabled extension).
- **Failures are contained.** A module that fails to import, or whose hook
  raises, is logged with `logger.exception` and the server keeps booting.
  This mirrors the tolerant behavior of the `urls/__init__.py` hub.
- **The middleware chain is already frozen.** `WSGIHandler.__init__` /
  `ASGIHandler.__init__` call `load_middleware()` during
  `get_*_application()`, *before* any extension hook runs. An extension
  that appends to `settings.MIDDLEWARE` (like `DjangoInstrumentor`) has no
  effect on the running handler until the chain is rebuilt — call
  `application.load_middleware()` in the hook (see the otel example
  below). This was a real regression: traces and metrics silently vanished
  while logs still worked.

The `extensions` package itself is base scaffold and always present in
generated projects, so the entrypoints import it plainly — a missing
`applications/extensions/` directory is a corrupted project and should fail
loudly at startup rather than boot silently with extensions disabled.

## Writing an extension

An extension is a plain module placed at
`<provider>/templates/applications/extensions/<name>.py` by a feature or
package. It may do side effects at import time or define a
`load(application)` hook:

```python
"""OpenTelemetry server extension — activates tracing, metrics, and logs."""

from collections.abc import Callable
from typing import Any

from django.core.handlers.asgi import ASGIHandler

from otel.setup import setup_otel


def load(application: Callable[..., Any]) -> None:
    setup_otel()
    # DjangoInstrumentor activates by appending its middleware to
    # settings.MIDDLEWARE, but the handler built its middleware chain inside
    # get_wsgi_application()/get_asgi_application(), before this hook ran.
    # Rebuild the chain so request spans and server metrics are produced.
    application.load_middleware(is_async=isinstance(application, ASGIHandler))
```

(That is the otel feature's extension, verbatim. `load_middleware()` fully
rebuilds the chain from `settings.MIDDLEWARE` and is safe to call again —
Django's own test client uses this pattern.)

### Wrapping the application (channels pattern)

An extension that needs to replace the served application rebinds the
entrypoint module's `application` attribute. The server resolves
`applications.asgi:application` *after* the module finishes importing, so the
wrapper is picked up. Hook return values are ignored, and every hook receives
the entrypoint's original handler instance, so a wrapping extension never
hides the handler from other extensions:

```python
"""Channels server extension — adds websocket routing to the ASGI app."""

from collections.abc import Callable
from typing import Any

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator


def load(application: Callable[..., Any]) -> None:
    import applications.asgi as asgi_module

    from ws_urls import websocket_urlpatterns

    asgi_module.application = ProtocolTypeRouter(
        {
            "http": asgi_module.application,
            "websocket": AllowedHostsOriginValidator(
                AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
            ),
        }
    )
```

This replaces the older pattern where packages shipped a full
`applications/asgi.py` override plus `restore_on_remove` — no scaffold file
is ever overwritten, removal is just file cleanup, and the imports now happen
*after* `django.setup()` instead of before it.

## Choosing between the mechanisms

| Need | Mechanism |
|------|-----------|
| Add/adjust settings for every process | `settings/apps/` or `settings/packages/` include |
| Register URL routes for every request | `urls/apps/` or `urls/packages/` include |
| Register WebSocket routes | `ws_urls/` include |
| Run code only in server processes (instrumentation, app wrapping) | `applications/extensions/` module |
| Run code when any app loads (signals, checks) | `AppConfig.ready()` in the feature's own Django app |

A note on the last row vs the fourth: `AppConfig.ready()` is tempting for
instrumentation, but it runs in **every** management command too — a
`startapp` or `migrate` that initializes exporters (and their atexit
shutdown paths) is how `ddx create app` used to hang against a stopped
collector. Keep `ready()` for things that must exist app-wide, and put
anything server-only in an extension.

## Testing expectations

Follow the pattern in `tests/features/test_otel.py` /
`tests/packages/test_channels.py`: assert the extension module exists after
install with the expected content, assert it is gone after remove, and
assert the base `applications/asgi.py` / `wsgi.py` still match
`djdevx/new/templates/` byte-for-byte.
