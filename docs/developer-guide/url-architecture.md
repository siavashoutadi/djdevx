# URL Architecture

## Overview

The generated Django project uses a **decentralised auto-discovery pattern**
for URL configuration. Instead of editing a monolithic `urls.py`, every
sub-module placed under the `urls/` directory that exports a `urlpatterns`
list is automatically discovered and merged into the root URLconf. This lets
packages, apps, and Django core each contribute URL patterns independently
without merge conflicts.

The same pattern is used for **WebSocket URLs**: modules under `ws_urls/`
that export a `websocket_urlpatterns` list are auto-discovered for use with
Django Channels.

---

## Project Structure

The generated project's URL directory is organised into three subdirectories,
each with a distinct purpose:

```
backend/
└── <backend_root>/
    ├── urls/
    │   ├── __init__.py          ← Auto-discovery hub
    │   ├── django/
    │   │   ├── __init__.py
    │   │   ├── admin.py         → path("admin/", admin.site.urls)
    │   │   └── media.py         → static() serving in DEBUG only
    │   ├── apps/
    │   │   ├── __init__.py
    │   │   ├── pwa.py           → path("", include("pwa.urls"))
    │   │   ├── tailwind_ui.py   → path("twui/", include(...))
    │   │   └── <app_name>.py    → path("<app_name>/", include("<app_name>.urls"))
    │   └── packages/
    │       ├── __init__.py
    │       ├── django_health_check.py    → health check endpoint
    │       ├── django_silk.py            → path("silk/", include("silk.urls"))
    │       ├── drf_spectacular.py        → api/schema/, swagger-ui/, redoc/
    │       └── ...                       (one file per installed third-party package)
    ├── ws_urls/                         ← WebSocket URL auto-discovery
    │   ├── __init__.py                  ← Same rglob + importlib pattern
    │   └── ...                          (package websocket_urlpatterns files)
    └── asgi.py                          → URLRouter(websocket_urlpatterns)
```

| Directory | Purpose | Managed by |
|-----------|---------|------------|
| `urls/django/` | Django core URLs (admin, media, static files) | Scaffolded once at project creation |
| `urls/apps/` | Custom Django app URLs | `ddx backend django create` or manual |
| `urls/packages/` | Third-party package URLs | `ddx backend django packages <name> install` / `remove` |
| `ws_urls/` | WebSocket URL patterns (Channels) | Package templates (e.g. channels) |

---

## The Auto-Discovery Hub

### HTTP URLs (`urls/__init__.py`)

```python
import importlib
from pathlib import Path

URLS_DIR = Path(__file__).parent

url_files = [str(f) for f in Path(URLS_DIR).rglob("*.py") if f.name != "__init__.py"]

urlpatterns = []

for file_path in url_files:
    relative_path = Path(file_path).relative_to(URLS_DIR).with_suffix("")
    module_name = f"urls.{'.'.join(relative_path.parts)}"

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "urlpatterns"):
            urlpatterns += module.urlpatterns
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
```

**How it works:**

1. `rglob("*.py")` walks every subdirectory under `urls/` (recursively).
2. Files named `__init__.py` are skipped (they're package markers, not URL
   modules).
3. Each remaining `.py` file is imported by its dotted module path
   (e.g. `urls.django.admin`, `urls.packages.django_health_check`).
4. If the imported module has a `urlpatterns` attribute, its contents are
   appended to the main `urlpatterns` list.
5. Import errors are printed to stdout but don't crash the server.

> **Result:** dropping a new `.py` file anywhere under `urls/` with a
> `urlpatterns` list is **all it takes** to register new URLs. No manual
> `include()` calls, no editing the root URLconf.

### WebSocket URLs (`ws_urls/__init__.py`)

The same pattern is used for WebSocket routing with Django Channels:

```python
import importlib
from pathlib import Path
from django.urls import URLPattern, URLResolver
from typing import List, Union

WS_URLS_DIR = Path(__file__).parent

ws_url_files = [
    str(f) for f in Path(WS_URLS_DIR).rglob("*.py") if f.name != "__init__.py"
]

websocket_urlpatterns: List[Union[URLPattern, URLResolver]] = []

for file_path in ws_url_files:
    relative_path = Path(file_path).relative_to(WS_URLS_DIR).with_suffix("")
    module_name = f"ws_urls.{'.'.join(relative_path.parts)}"

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "websocket_urlpatterns"):
            websocket_urlpatterns.extend(module.websocket_urlpatterns)
    except Exception as e:
        print(f"Error importing WebSocket URL patterns from {module_name}: {e}")

__all__ = ["websocket_urlpatterns"]
```

The ASGI config (`asgi.py`) then wraps these in a `URLRouter`:

```python
from ws_urls import websocket_urlpatterns

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})
```

---

## URL Subdirectory Roles

### `urls/django/` — Django Core

Holds URLs for Django's built-in functionality:

- **`admin.py`** — registers `path("admin/", admin.site.urls)`
- **`media.py`** — serves `MEDIA_URL` via `static()` when `DEBUG = True`

These are scaffolded once when the project is created and rarely change.

### `urls/apps/` — Custom Django Apps

Holds URL configuration for custom Django applications. There are two ways
an app gets its URL file here:

#### Via `ddx backend django create`

When you run:

```
ddx backend django create --application-name myapp
```

The startapp feature copies a Jinja2 template to produce two files:

1. **App-level URL file** (`urls/apps/myapp.py`):
   ```python
   from django.urls import include, path

   urlpatterns = [
       path("myapp/", include("myapp.urls")),
   ]
   ```

2. **App URLconf** (`myapp/urls.py`):
   ```python
   from django.urls import path
   from .views import index

   urlpatterns = [
       path("", index, name="myapp"),
   ]
   ```

Because `urls/apps/myapp.py` exports `urlpatterns`, it is automatically
picked up by the auto-discovery hub — no manual wiring needed.

#### Manually

Create `urls/apps/<app_name>.py` with a standard `urlpatterns` list. The
auto-discoverer will pick it up on the next server reload.

### `urls/packages/` — Third-Party Packages

URL files for third-party packages installed via djdevx. Each installed
package contributes one file here, auto-derived from the package's module
location (see [Path Auto-Derivation](#path-auto-derivation)).

---

## How Packages Contribute URLs

### Template Location Convention

Package URL templates live at:

```
djdevx/templates/django/<template_path>/urls/packages/<derived_name>.py[.j2]
```

Where `<derived_name>` is auto-derived from the package's Python module
location by `PathDeriver`.

### Path Auto-Derivation

`PathDeriver` (`_base.py:22`) computes `url_file` from the package
module's file path:

| Package location | Derived `url_file` | Rendered to project |
|---|---|---|
| `packages/whitenoise.py` | `whitenoise.py` | `urls/packages/whitenoise.py` |
| `packages/django_health_check.py` | `django_health_check.py` | `urls/packages/django_health_check.py` |
| `packages/django_allauth/account.py` | `django_allauth_account.py` | `urls/packages/django_allauth_account.py` |
| `packages/django_storages/s3.py` | `django_storages_s3.py` | `urls/packages/django_storages_s3.py` |

**Rule:**
- **Root packages** (`packages/<name>.py`) → `<name>.py`
- **Sub-packages** (`packages/<dir>/<name>.py`) → `<dir>_<name>.py`

### Explicit Override

Set `url_file` on the `BasePackage` subclass when the derived name would
conflict with another package's file (unusual — only needed for collisions):

```python
class MyPackage(BasePackage):
    name = "my-package"
    packages = ["my-package"]
    url_file = "custom_url_filename.py"   # → urls/packages/custom_url_filename.py
```

### Install Flow

1. `BasePackage.install()` calls `_copy_templates()`.
2. `TemplateManager` walks the package's `templates/django/<name>/` directory.
3. Files with `.j2` suffix are rendered through Jinja2 (the `.j2` extension
   is stripped from the output filename).
4. Non-`.j2` files are copied verbatim.
5. The rendered/copied file lands in the project's `urls/packages/`
   directory.
6. The auto-discovery hub picks it up automatically.

### Uninstall Flow

When a package is removed, `BasePackage._cleanup_files()` deletes the
auto-derived URL file:

```python
def _cleanup_files(self) -> None:
    settings_path = self.pm.packages_settings_path / self._settings_file
    settings_path.unlink(missing_ok=True)

    url_path = self.pm.packages_urls_path / self._url_file
    url_path.unlink(missing_ok=True)
```

---

## Conditional URL Patterns

Many packages should only register URLs in certain environments. The common
patterns are:

### DEBUG-only

```python
from settings.django.base import DEBUG
from django.urls import path, include

if DEBUG:
    urlpatterns = [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
```

Used by: `django_browser_reload`, `djangorestframework` (api-auth),
`tailwind_ui`

### DEBUG + not TESTING

```python
import sys
from settings.django.base import DEBUG

TESTING = "test" in sys.argv

if DEBUG and not TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns = debug_toolbar_urls()
```

Used by: `django_debug_toolbar`

### not TESTING

```python
import sys
from django.urls import path, include

TESTING = "test" in sys.argv

if not TESTING:
    urlpatterns = [
        path("silk/", include("silk.urls", namespace="silk")),
    ]
else:
    urlpatterns = []
```

Used by: `django_silk`

### Environment-dependent endpoints (DEBUG vs production)

```python
from settings.django.base import DEBUG
from django.urls import path, include
import oauth2_provider.views as oauth2_views

oauth2_endpoint_views = [
    path("authorize/", oauth2_views.AuthorizationView.as_view(), name="authorize"),
    path("token/", oauth2_views.TokenView.as_view(), name="token"),
    path("revoke-token/", oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if DEBUG:
    oauth2_endpoint_views += [
        path("applications/", oauth2_views.ApplicationList.as_view(), ...),
        # ... more dev-only endpoints
    ]

urlpatterns = [
    path("o/", include((oauth2_endpoint_views, "oauth2_provider"), namespace="oauth2_provider")),
]
```

Used by: `django_oauth_toolkit`

---

## Parameterised URLs with Jinja2

When a package declares `install_params`, the collected values are available
in URL templates as Jinja2 variables. The template file must use the `.j2`
extension to trigger rendering.

### Example: django-allauth account

**Template** (`templates/django/django_allauth/account/urls/packages/django_allauth_account.py.j2`):

```python
from django.urls import path, include

urlpatterns = [
    path("{{ account_url_prefix }}/", include("allauth.urls")),
]
```

At install time, the user is prompted for `account_url_prefix`:

```
ddx backend django packages django-allauth account install --account-url-prefix auth
```

The rendered output becomes `urls/packages/django_allauth_account.py`:

```python
from django.urls import path, include

urlpatterns = [
    path("auth/", include("allauth.urls")),
]
```

### Example: startapp (app creator)

**Template** (`templates/django/startapp/urls/apps/{{application_name}}.py.j2`):

```python
from django.urls import include, path

urlpatterns = [
    path("{{ application_name }}/", include("{{application_name}}.urls")),
]
```

Note that both the **file name** and the **file contents** use Jinja2
expressions. The `TemplateManager` renders both — `{{application_name}}.py.j2`
becomes `<app_name>.py` with the content rendered with the same context.

---

## WebSocket URLs

WebSocket URL patterns follow the identical auto-discovery pattern via
`ws_urls/__init__.py`. The main difference is that modules under `ws_urls/`
are expected to export `websocket_urlpatterns` instead of `urlpatterns`.

### Example: channels package

The `channels` package template provides a `ws_urls/__init__.py` that
auto-discovers all WebSocket patterns, and an `asgi.py` that wires them
into the ASGI application:

```python
# asgi.py
from ws_urls import websocket_urlpatterns

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})
```

---

## How to Add URLs for Your Own App

### Option 1: Use `ddx backend django create`

The simplest approach. Running:

```
ddx backend django create --application-name myapp
```

Automatically:
1. Runs `python manage.py startapp myapp`
2. Creates `urls/apps/myapp.py` with `path("myapp/", include("myapp.urls"))`
3. Creates `myapp/urls.py` with a basic index view URL

Both files are auto-discovered — no further configuration needed.

### Option 2: Manual

1. Create `urls/apps/<app_name>.py`:
   ```python
   from django.urls import include, path

   urlpatterns = [
       path("<url_prefix>/", include("<app_name>.urls")),
   ]
   ```

2. Ensure your app has a `urls.py` that exports `urlpatterns`.

That's it. The auto-discovery hub in `urls/__init__.py` will find and
register the patterns on the next server reload.

---

## How to Add URLs for a Package

To make a new djdevx package contribute URL patterns:

### Step 1: Create the URL template

```
djdevx/templates/django/<template_path>/urls/packages/<url_file>.py.j2
```

Where `<template_path>` and `<url_file>` follow the auto-derivation rules
(see [Path Auto-Derivation](#path-auto-derivation)).

### Step 2: Add URL patterns

For a simple package:

```python
# templates/django/my_package/urls/packages/my_package.py.j2
from django.urls import path, include

urlpatterns = [
    path("my-endpoint/", include("my_package.urls")),
]
```

For a package with install-time configuration (use `.j2` extension):

```python
# templates/django/my_package/urls/packages/my_package.py.j2
from django.urls import path, include

urlpatterns = [
    path("{{ url_prefix }}/", include("my_package.urls")),
]
```

### Step 3: Ensure the template exists

Templates are optional — if the `templates/django/<template_path>/`
directory does not exist, template copying is silently skipped. Make sure
your directory structure is correct.

### Step 4: Use conditional guards when appropriate

If your package should only register URLs in DEBUG mode, in production, or
when not running tests, use the guard patterns shown in
[Conditional URL Patterns](#conditional-url-patterns).

### Step 5: Override `url_file` if needed

If the auto-derived filename would collide with another package's URL file,
set `url_file` on your `BasePackage` subclass:

```python
class MyPackage(BasePackage):
    name = "my-package"
    packages = ["my-package"]
    url_file = "unique_name.py"
```

### What happens at install/remove

- **Install**: `_copy_templates()` renders the `.j2` file and writes it to
  the project's `urls/packages/` directory. The auto-discovery hub picks it up.
- **Remove**: `_cleanup_files()` deletes `urls/packages/<url_file>`. The
  URL patterns are automatically removed.

---

## URL Namespacing

Package URL patterns should use Django's URL namespacing to prevent
collisions between packages that define the same URL prefix names:

```python
urlpatterns = [
    path("silk/", include("silk.urls", namespace="silk")),
]
```

This is a Django-level convention — the auto-discovery system does not
impose any namespacing requirements. As long as each `.py` file exports a
`urlpatterns` list, it will be merged into the root URLconf regardless
of namespace declarations.

---

## Related

- [Package Architecture](package-architecture.md) — How packages declare
  URLs via `BasePackage`, `url_file`, and `PathDeriver`
- [Creating a Package](creating-a-package.md) — Step-by-step guide for
  adding a new Django package to djdevx
- [Template System](template-system.md) — Jinja2 rendering, `.j2`
  conventions, and template context
- [Pydantic Settings Architecture](pydantic-settings.md) — How settings
  templates complement URL templates in a package
