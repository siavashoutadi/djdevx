# Framework Architecture

Frameworks manage CSS/JS libraries (Bootstrap, Franken UI, Semantic UI) that
are injected into the Django project's `_base.html` template.

## BaseFramework

`BaseFramework` (`djdevx/providers/frameworks/_base.py`) is a thin subclass of
the shared `Provider` base (`djdevx/provider.py`) pinned to `FRAMEWORK_KIND`;
CSS/JS download and template injection live in the generic `CSSFramework` /
`CSSFrameworkProviderMixin` scaffolding, not in the payload classes.

### Additional Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `css_assets` | `list[Asset]` | CDN CSS files to vendor (`Asset(url=..., filename=...)`) |
| `js_assets` | `list[Asset]` | CDN JS files to vendor |
| `js_module` | `bool` | If `True`, adds `type="module"` to the `<script>` tags |

### Lifecycle

Frameworks use the standard `Installable` lifecycle with custom behavior
in two hook overrides:

```
add:
  1. before_pixi_install()
  2. PixiOps(root).add_packages()
  3. after_pixi_install()
  4. before_copy_templates()
  5. scaffold.copy_templates()
  6. after_copy_templates()           ← downloads CSS/JS, modifies _base.html
  7. SecretsOps(root).generate()
  8. TrackingOps(section).track_install()

remove:
  1. before_pixi_remove()             ← removes CSS/JS tags from _base.html
  2. PixiOps(root).remove_packages()
  3. after_pixi_remove()
  4. scaffold.cleanup_files()         ← deletes CSS/JS files from static/
  5. SecretsOps(root).remove()
  6. scaffold.restore_originals()
  7. TrackingOps(section).remove()
```

### CSS/JS Injection

When `after_copy_templates()` runs:

1. For each entry in `css_assets`, downloads the file to `static/css/vendor/<filename>`
2. For each entry in `js_assets`, downloads the file to `static/js/vendor/<filename>`
3. Inserts a `<link>` tag before `</head>` in `templates/_base.html` per CSS asset
4. Inserts a `<script>` tag before `</body>` in `templates/_base.html` per JS asset

On remove, `before_pixi_remove()` reverses the injection by removing the tags
and deleting the downloaded files.

### Generated Tags

```html
<!-- CSS -->
<link rel="stylesheet" href="{% static 'css/vendor/<asset.filename>' %}">

<!-- JS -->
<script src="{% static 'js/vendor/<asset.filename>' %}"></script>
<!-- or with js_module=True -->
<script type="module" src="{% static 'js/vendor/<asset.filename>' %}"></script>
```

### Concrete Implementations

All frameworks follow the same minimal pattern — declare attributes and
nothing else:

```python
@register
class BootstrapFramework(CSSFramework):
    name: str = "bootstrap"
    display_name: str = "Bootstrap"
    description: str = "Bootstrap CSS/JS framework"
    css_assets: list[Asset] = [
        Asset(
            url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
            filename="bootstrap.min.css",
        ),
    ]
    js_assets: list[Asset] = [
        Asset(
            url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
            filename="bootstrap.bundle.min.js",
        ),
    ]
```

```python
@register
class FrankenUIFramework(CSSFramework):
    name: str = "frankenui"
    display_name: str = "Franken UI"
    css_assets: list[Asset] = [
        Asset(
            url="https://cdn.jsdelivr.net/npm/franken-ui@2.1.2/dist/css/core.min.css",
            filename="franken-core.css",
        ),
        Asset(
            url="https://cdn.jsdelivr.net/npm/franken-ui@2.1.2/dist/css/utilities.min.css",
            filename="franken-utilities.css",
        ),
    ]
    js_assets: list[Asset] = [
        Asset(
            url="https://cdn.jsdelivr.net/npm/franken-ui@2.1.2/dist/js/core.iife.js",
            filename="franken-core.js",
        ),
        Asset(
            url="https://cdn.jsdelivr.net/npm/franken-ui@2.1.2/dist/js/icon.iife.js",
            filename="franken-icon.js",
        ),
    ]
    js_module: bool = True
```

No overrides of hooks are needed — `BaseFramework` handles everything through
its built-in `after_copy_templates()` and `before_pixi_remove()`.

## CLI Commands

```
ddx frameworks add [NAME] [-v]       # Install a framework
ddx frameworks remove [NAME] [-v]    # Remove a framework
ddx frameworks list                   # List all frameworks
```

Frameworks do not support variants, so there is no `--provider` flag.

## Related

- [Installable System](installable-system.md) — Shared infrastructure
- [Add a Framework](adding-a-framework.md) — Step-by-step guide
- [Template System](template-system.md) — Jinja2 rendering
