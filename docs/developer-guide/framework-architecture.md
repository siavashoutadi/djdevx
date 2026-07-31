# Framework Architecture

Frameworks manage CSS/JS libraries (Bootstrap, Franken UI, Semantic UI) that
are injected into the Django project's `_base.html` template.

## BaseFramework

`BaseFramework` (`djdevx/frameworks/_base.py`) extends `Installable` with
`section: str = "frameworks"` and CSS/JS-specific attributes and template
injection logic.

### Additional Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `css_url` | `str` | URL to download the CSS file from |
| `css_filename` | `str` | Local filename for the CSS file |
| `js_url` | `str` | URL to download the JS file from |
| `js_filename` | `str` | Local filename for the JS file |
| `js_module` | `bool` | If `True`, adds `type="module"` to the `<script>` tag |

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

1. If `css_url` is set, downloads the CSS file to `static/css/<css_filename>`
2. If `js_url` is set, downloads the JS file to `static/js/<js_filename>`
3. Inserts `<link>` tag before `</head>` in `templates/_base.html`
4. Inserts `<script>` tag before `</body>` in `templates/_base.html`

On remove, `before_pixi_remove()` reverses the injection by removing the tags
and deleting the downloaded files.

### Generated Tags

```html
<!-- CSS -->
<link rel="stylesheet" href="{% static 'css/<css_filename>' %}">

<!-- JS -->
<script src="{% static 'js/<js_filename>' %}"></script>
<!-- or with js_module=True -->
<script type="module" src="{% static 'js/<js_filename>' %}"></script>
```

### Concrete Implementations

All frameworks follow the same minimal pattern — declare attributes and
nothing else:

```python
@register
class BootstrapFramework(BaseFramework):
    name: str = "bootstrap"
    display_name: str = "Bootstrap"
    description: str = "Bootstrap CSS/JS framework"
    css_url: str = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    css_filename: str = "bootstrap.min.css"
    js_url: str = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
    js_filename: str = "bootstrap.bundle.min.js"
```

```python
@register
class FrankenUIFramework(BaseFramework):
    name: str = "frankenui"
    display_name: str = "Franken UI"
    css_url: str = "https://cdn.jsdelivr.net/npm/franken-ui@1.0.3/dist/css/franken-ui.min.css"
    css_filename: str = "franken.css"
    js_url: str = "https://cdn.jsdelivr.net/npm/franken-ui@1.0.3/dist/js/franken-ui.min.js"
    js_filename: str = "franken.js"
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
