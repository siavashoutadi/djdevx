# Adding a Feature

Step-by-step guide to adding a new feature to djdevx. Features are
higher-level components that may span multiple packages and templates (e.g.,
PWA support, a Tailwind theme, Tailwind UI components).

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
9. [Testing](#testing)

---

## How features differ from packages

- Features are **not** tied to a single third-party package — they often
  declare **no `pixi_packages` at all** (`pwa`, `tailwind_ui`,
  `tailwind_theme`) and exist purely for template/config wiring.
- When a feature does need a package, it declares a **dependency on another
  djdevx installable** via `needs` — the orchestrator auto-installs it first.
- Features use hooks (rather than `InstallParam`-driven class config) for
  custom behavior.

## Minimal feature

```python
# djdevx/features/pwa/__init__.py
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
# djdevx/features/tailwind_ui/__init__.py
from ...utils.installable.types import InstallableRef, PACKAGE

from .._base import BaseFeature
from .._registry import register


@register
class TailwindUIFeature(BaseFeature):
    name: str = "tailwind_ui"
    display_name: str = "Tailwind UI"
    description: str = "Tailwind UI components (alerts, badges, buttons, toasts, cards)"
    needs: list[InstallableRef] = [InstallableRef("django-tailwind-cli", PACKAGE)]
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
    InstallParam(name="icon_path", default="static/images/logo.svg",
                 prompt="Path to the icon file to be used for generating the PWA icons"),
    InstallParam(name="background_color", default="#ffffff",
                 prompt="Please enter the background color of the application"),
    InstallParam(name="theme_color", default="#000000",
                 prompt="Please enter the theme color of the application"),
]
```

`tailwind_theme` shows a long list of 16 params with color defaults (light and
dark theme palettes).

## Enriching the install context

Use `before_copy_templates()` to derive new context keys before templates are
rendered. `tailwind_theme` generates a full color palette for each collected
color and rewrites `--color-*` values to `var(--color-*)`:

```python
# djdevx/features/tailwind_theme/__init__.py
@register
class TailwindThemeFeature(BaseFeature):
    name: str = "tailwind_theme"
    display_name: str = "Tailwind Theme"

    def _enrich_context(self) -> None:
        ctx = self._install_context
        for color_key, palette_key in {
            "primary_color": "primary_palette",
            "secondary_color": "secondary_palette",
        }.items():
            hex_val = ctx.get(color_key, "")
            ctx[palette_key] = color_converter.generate_palette(hex_val)

    def before_copy_templates(self) -> None:
        self._enrich_context()

    def after_copy_templates(self) -> None:
        input_css = self.structure.tailwind_input_css
        if input_css.exists():
            content = input_css.read_text()
            if '@import "./theme.css";' not in content:
                content = '@import "./theme.css";\n' + content
                input_css.write_text(content)

    def before_pixi_remove(self) -> None:
        input_css = self.structure.tailwind_input_css
        if input_css.exists():
            content = input_css.read_text()
            content = content.replace('@import "./theme.css";\n', "")
            input_css.write_text(content)
```

The derived palette keys are then available as Jinja2 variables in templates
and in later hooks via `self._install_context`.

## Generating files in hooks

`pwa` is the heavyweight example: `after_copy_templates()` generates ~150 PNG
icons and splash screens from the source icon (via PIL), writes the web app
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
djdevx/features/<name>/
├── __init__.py
└── templates/
    ├── settings/
    │   └── apps/
    │       └── <name>.py.j2
    └── urls/
        └── apps/
            └── <name>.py.j2
```

Templates render to the project root.

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
- [Feature Architecture](feature-architecture.md) — BaseFeature details
- [Installable System](installable-system.md) — Shared infrastructure
- [Template System](template-system.md) — Jinja2 rendering conventions
