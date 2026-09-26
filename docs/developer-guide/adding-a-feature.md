# Adding a Feature

Step-by-step guide to adding a new feature to djdevx. Features are
higher-level components that may span multiple packages and templates (e.g.,
PWA support).

This page focuses on feature-specific concerns. Shared concepts (variants,
install params, secrets, hooks, templates, testing) live in
[Common Concepts](creating-an-installable.md).

## Table of Contents

1. [How features differ from packages](#how-features-differ-from-packages)
2. [Minimal feature](#minimal-feature)
3. [Depending on a package (needs)](#depending-on-a-package-needs)
4. [Install params](#install-params)
5. [Enriching the install context](#enriching-the-install-context)
6. [Generating files in hooks](#generating-files-in-hooks)
7. [Variants](#variants)
8. [Feature templates directory](#feature-templates-directory)
9. [Peer integration](#peer-integration)
10. [SDK-backed observability features](#sdk-backed-observability-features)
11. [Testing](#testing)

---

## How features differ from packages

- Features are **not** tied to a single third-party package — they often
  declare **no `pixi_packages` at all** (`pwa`) and exist purely for
  template/config wiring.
- When a feature does need a package, it declares a **dependency on another
  djdevx installable** via `needs` — the orchestrator auto-installs it first.
- Features use hooks (rather than `InstallParam`-driven class config) for
  custom behavior.

## Minimal feature

```python
# djdevx/providers/features/pwa/__init__.py
from .._base import BaseFeature
from .._registry import register


@register
class PWAFeature(BaseFeature):
    name: str = "pwa"
    display_name: str = "PWA"
    description: str = "Progressive Web App support with service worker and manifest"
```

## Depending on a package (needs)

Features commonly need another installable present. `needs` accepts
`InstallableRef` entries with an `InstallableKind` (usually `PACKAGE`), and
dependencies are auto-installed recursively before the feature:

```python
# djdevx/providers/features/sso/__init__.py
from ...utils.installable.types import InstallableRef, PACKAGE

from .._base import BaseFeature
from .._registry import register


@register
class SSOFeature(BaseFeature):
    name: str = "sso"
    display_name: str = "Single Sign-On"
    description: str = "Authentication via third-party identity providers"
    needs: list[InstallableRef] = [InstallableRef("django-allauth", PACKAGE)]
```

Cross-category dependencies work in both directions — a feature can depend on
a package, a database, another feature, etc. See
[Dependencies (needs)](creating-an-installable.md#dependencies-needs).

## Install params

Features collect install-time parameters exactly like packages. `pwa` collects
12 params, including paths and colors with defaults:

```python
from ...utils.installable.types import InstallParam

install_params: list[InstallParam] = [
    InstallParam(name="app_name", prompt="Please enter the display name for the application"),
    InstallParam(name="icon_path", default="static/images/logo.png",
                 prompt="Path to the icon file to be used for generating the PWA icons (PNG/JPEG)"),
    InstallParam(name="background_color", default="#ffffff",
                 prompt="Please enter the background color of the application"),
    InstallParam(name="theme_color", default="#000000",
                 prompt="Please enter the theme color of the application"),
]
```

## Enriching the install context

Use `before_copy_templates()` to derive new context keys before templates are
rendered. For example, resolving a user-supplied relative path into values
templates can use directly:

```python
# djdevx/providers/features/sso/__init__.py
@register
class SSOFeature(BaseFeature):
    name: str = "sso"
    display_name: str = "Single Sign-On"

    def _enrich_context(self) -> None:
        ctx = self._install_context
        callback_url = ctx.get("callback_url", "")
        if callback_url and not callback_url.startswith("/"):
            ctx["callback_url"] = "/" + callback_url

    def before_copy_templates(self) -> None:
        self._enrich_context()
```

The derived keys are then available as Jinja2 variables in templates and in
later hooks via `self._install_context`.

## Generating files in hooks

`pwa` is the heavyweight example: `before_pixi_install()` validates the icon
and aborts the install (before anything is changed) when the icon file is
missing, empty, or not a readable raster image (SVG is rejected — provide a
PNG/JPEG). `after_copy_templates()` then generates ~150 PNG icons and splash
screens from the source icon (via PIL), writes the web app
manifest, writes `templates/apple_splash.html`, and injects the manifest link
into `_base.html`. `before_pixi_remove()` removes the injected lines.

Because programmatically generated files are **not** tracked by
`cleanup_files` (only template copies are), they must be declared explicitly:

```python
files_to_remove: list[str] = [
    "pwa/templates/manifest.json",
    "templates/apple_splash.html",
]
folders_to_remove: list[str] = [
    "static/images/icons/android",
    "static/images/icons/ios",
    "static/images/icons/windows11",
    "static/images/icons/splash_screens",
]
```

Read install-time values from `self._install_context` inside hooks — e.g. `pwa`
resolves `icon_path` relative to the project root:

```python
def _resolve_icon_path(self) -> Path | None:
    icon_path = self._install_context.get("icon_path", "")
    if not icon_path:
        return None
    path = Path(icon_path)
    if not path.is_absolute():
        path = self.structure.root / path
    return path if path.exists() else None
```

## Variants

Features support the same variant system as packages — exclusive
(`exclusive_variants=True`) for mutually exclusive options, additive for
optional sub-features. See
[Working with Variants](creating-an-installable.md#working-with-variants).

```python
@register
class SSOFeature(BaseFeature):
    name: str = "sso"
    display_name: str = "Single Sign-On"
    exclusive_variants: bool = True
    variants: dict[str, Variant] = {
        "google": Variant(
            name="google",
            display_name="Google SSO",
            pixi_packages=[PixiPackageSpec("django-allauth[socialaccount]")],
        ),
        "github": Variant(
            name="github",
            display_name="GitHub SSO",
            pixi_packages=[PixiPackageSpec("django-allauth[socialaccount]")],
        ),
    }
```

## Feature templates directory

```
djdevx/providers/features/<name>/
├── __init__.py
└── templates/
    ├── settings/
    │   └── apps/
    │       └── <name>.py.j2
    ├── urls/
    │   └── apps/
    │       └── <name>.py.j2
    └── peer_templates/
        └── <peer>/
            └── settings/
                └── apps/
                    └── <name>_<peer>.py
```

Templates render to the project root.

Name a template `<name>.py.j2` only when it needs template variables (for
example, otel's settings file renders the project name into the service name).
A settings module with nothing to render should stay a plain `.py` — a `.j2`
with no placeholders is misleading.

`peer_templates/<peer>/` is copied in and out automatically when that peer
installable is added or removed, in either order relative to the feature. Peer
templates do not need a `__init__.py`: settings files are executed by filename
in a shared namespace, and the plugin packages that need one ship it in the
feature's own templates tree.

## Peer integration

Features can declare `peer_pixi_packages` to add pixi dependencies only when a
specific peer is installed. The engine adds/removes them during `add`/`remove`.
For more complex adaptation, override `on_peer_added` / `on_peer_removed`.

```python
# djdevx/providers/features/my_instrumentation/__init__.py
from .._base import BaseFeature
from ...utils.installable.types import InstallableRef, DATABASE
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class MyInstrumentationFeature(BaseFeature):
    name: str = "my-instrumentation"
    display_name: str = "My Instrumentation"
    peer_pixi_packages: dict[InstallableRef, list[PixiPackageSpec]] = {
        InstallableRef("postgres", DATABASE): [PixiPackageSpec("my-db-instrumentation", kind="pypi")],
    }

    def on_peer_added(self, peer, variant=None) -> None:
        # append an instrumentation snippet to my own settings artifact
        self._write_snippet(peer.name)

    def on_peer_removed(self, peer, variant=None) -> None:
        self._remove_snippet(peer.name)
```

Install the feature before or after the database — the same hooks fire either
way, and removing either side cleans up both snippets and peer packages.
See [Integration Protocol](integration.md) for full semantics.

## SDK-backed observability features

`sentry` is the reference for a feature that wraps a third-party SDK: the SDK
initiates instrumentation itself, and djdevx only supplies the app, the settings,
and the peer wiring. Three decisions are worth copying.

**Initialize from `AppConfig.ready()`, not an install param or a server-only
extension.** `ready()` runs exactly once per process — web server, Celery
worker, Celery Beat, management commands — and Django's app registry is
populated before a Celery worker executes any task, which is exactly the
"initialize on worker startup" requirement these SDKs document. A
`applications/extensions/` module is server-only and would miss workers
entirely. See [Extensions Architecture](extensions-architecture.md).

```python
# templates/sentry/apps.py
class SentryConfig(AppConfig):
    name = "sentry"

    def ready(self) -> None:
        from sentry.setup import setup_sentry

        setup_sentry()
```

The setup function must be **idempotent** (module-level guard) and must **never
raise** — a broken or unreachable monitoring backend must not take the app
registry down with it. `sentry/setup.py` logs and returns instead.

**Declare required secrets without prompting, and say so at install time.** A
required `SecretStr` with no default is the right call for a DSN: a placeholder
would silently drop every event. `SecretsOps.generate()` only handles registered
generators, so the feature declares none and the operator supplies the value.
That makes Django un-importable until they act, so the install hook must print
the exact command:

```python
def after_copy_templates(self, step: NestedStep | None = None) -> None:
    (step.warning if step else print_console.warning)(
        "Sentry DSN is required but was not configured"
    )
    for line in (...):
        (step.info if step else print_console.info)(line)
```

Feature removal deliberately does **not** delete the resulting
`.secrets/<name>` file: it was entered by hand, so deleting it would destroy a
value the project still needs on reinstall. Only `secret_generators` output is
cleaned up automatically.

**Use hook-only peers, and detect them from the settings namespace.** When the
SDK already bundles the integration, the peer needs no packages at all — an
empty list still triggers `peer_templates/` synchronization:

```python
peer_pixi_packages: dict[InstallableRef, list[PixiPackageSpec]] = {
    InstallableRef("celery", TASK_QUEUE): [],
    InstallableRef("celery-beat", SCHEDULER): [],
}
```

Celery is not in `INSTALLED_APPS` in a generated project, so there is nothing to
introspect. The peer settings module's exported constants are the activation
signal: `setup_sentry` checks `hasattr(settings, "SENTRY_CELERY_PROPAGATE_TRACES")`
and registers the integration only when that file is present. Keep the two peer
settings modules free of overlapping field names so the `SettingCollector` never
sees a duplicate.

Prefer the SDK's current API over deprecated flags (e.g. `capture_sentry_logs`
rather than the removed `enable_logs`), and verify kwarg names against the
installed SDK — a `DidNotEnable` raised by the SDK is a plain `Exception`, not
an `ImportError`, so a guarded import needs to catch both.

## Testing

```bash
ddx features add my-feature
ddx features list
ddx features remove my-feature
```

See [Testing](creating-an-installable.md#testing) for the CLI integration
test pattern and golden-file fixtures.

## Related

- [Common Concepts](creating-an-installable.md) — shared pattern, variants, params, hooks, templates
- [Integration Protocol](integration.md) — peer integration reference
- [Feature Architecture](feature-architecture.md) — BaseFeature details
- [Installable System](installable-system.md) — Shared infrastructure
- [Template System](template-system.md) — Jinja2 rendering conventions
