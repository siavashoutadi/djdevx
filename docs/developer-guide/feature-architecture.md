# Feature Architecture

Features are higher-level components that may span multiple packages and
templates (e.g., PWA support). They use the same
`Installable` base as packages but without `InstallParam` on variants
(though variants are still supported).

## BaseFeature

`BaseFeature` (`djdevx/features/_base.py`) extends `Installable` with
`section: str = "features"`.

### Additional Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `exclusive_variants` | `bool` | If `True`, user picks exactly one variant |
| `variants` | `dict[str, Variant]` | Named variants |
| `install_params` | `list[InstallParam]` | Parameters collected at install time |

### Variant

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier |
| `display_name` | `str` | Human-readable name |
| `required` | `bool` | Auto-installed when the feature is added |
| `pixi_packages` | `list[PixiPackageSpec]` | Variant-specific dependencies |
| `conditional_packages` | `list[ConditionalPackage]` | Variant-specific gated dependencies (conditions receive the parent installable) |
| `template_path` | `str` | Override template directory |
| `files_to_remove` | `list[str]` | Files to delete on uninstall |
| `folders_to_remove` | `list[str]` | Folders to delete on uninstall |
| `restore_on_remove` | `dict[str, str]` | Template overrides |

### Lifecycle

Features follow the standard `Installable` lifecycle:

```
add_installable(cls, name, provider=None):
  1. _auto_install_needs(needs)              ← recursively install dependencies
  2. Installable.add(variant_name, install_kwargs):
     a. before_pixi_install()                ← hook
     b. PixiOps(root).add_packages()         ← pixi add
     c. after_pixi_install()                 ← hook
     d. before_copy_templates()              ← hook
     e. scaffold.copy_templates()            ← Jinja2 render
     f. after_copy_templates()               ← hook (e.g. CSS modification)
     g. SecretsOps(root).generate()          ← auto-generate secrets
     h. TrackingOps(section).track_install() ← write tracking
```

### Difference from Packages

Features are identical to packages in architecture — they use the same
`Installable` base class. The only difference is semantic: features are
higher-level constructs (e.g., PWA) vs. third-party Django packages.

### Concrete Examples

Simple feature (no variants):

```python
@register
class PWAFeature(BaseFeature):
    name: str = "pwa"
    display_name: str = "PWA"
    description: str = "Progressive Web App support with service worker and manifest"

    install_params: list[InstallParam] = [
        InstallParam(name="app_name", prompt="Display name for the app"),
        InstallParam(name="short_name", prompt="Short name for the app"),
    ]
    files_to_remove: list[str] = [
        "pwa/templates/manifest.json",
        "templates/apple_splash.html",
    ]
    folders_to_remove: list[str] = [
        "static/images/icons/android",
        "static/images/icons/ios",
    ]

    def after_copy_templates(self) -> None:
        self._generate_icons()
        self._write_manifest()
        self._update_base_html()

    def before_pixi_remove(self) -> None:
        self._remove_from_base_html()
```

Feature with hook overrides:

```python
@register
class SSOFeature(BaseFeature):
    name: str = "sso"
    display_name: str = "Single Sign-On"
    needs: list[InstallableRef] = [InstallableRef("django-allauth", PACKAGE)]

    def after_copy_templates(self) -> None:
        urls_file = self.structure.packages_urls_dir / "sso.py"
        if not urls_file.exists():
            urls_file.write_text("from django.urls import path, include\n\nurlpatterns = []\n")

    def before_pixi_remove(self) -> None:
        (self.structure.packages_urls_dir / "sso.py").unlink(missing_ok=True)
```

## CLI Commands

```
ddx features add [NAME] [-p provider] [-v]
ddx features remove [NAME] [-p provider] [-v]
ddx features list
```

Features support variants with the same `--provider` flag as packages.

## Related

- [Installable System](installable-system.md) — Shared infrastructure
- [Add a Feature](adding-a-feature.md) — Step-by-step guide
- [Template System](template-system.md) — Jinja2 rendering
