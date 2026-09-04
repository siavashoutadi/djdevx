# Adding a Framework

Step-by-step guide to adding a new CSS/JS framework to djdevx. Frameworks
manage CSS/JS libraries that are injected into the Django project's
`_base.html` template. They are the simplest installable type — just declare
attributes and `BaseFramework` handles everything through the lifecycle.

This page focuses on framework-specific concerns. Shared concepts (variants,
install params, secrets, hooks, templates, testing) live in
[Common Concepts](creating-an-installable.md).

## Table of Contents

1. [Minimal framework](#minimal-framework)
2. [Framework attributes](#framework-attributes)
3. [ES module scripts (js_module)](#es-module-scripts-js_module)
4. [Lifecycle](#lifecycle)
5. [Full custom hooks](#full-custom-hooks)
6. [Framework templates](#framework-templates)
7. [Testing](#testing)

---

## Minimal framework

```python
# djdevx/providers/frameworks/bootstrap/__init__.py
from .._base import BaseFramework
from .._registry import register


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

That's it. Declaring the URLs and filenames is enough — `BaseFramework`
downloads the files into `static/css/vendor` / `static/js/vendor` and injects
the `<link>`/`<script>` tags into `_base.html`.

If the framework only needs CSS (no JS), leave `js_url`/`js_filename` empty.

## Framework attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier (used in CLI) |
| `display_name` | Yes | Human-readable name for CLI output |
| `description` | No | Longer description |
| `css_url` | No | URL to download CSS from |
| `css_filename` | No | Local filename for CSS |
| `js_url` | No | URL to download JS from |
| `js_filename` | No | Local filename for JS |
| `js_module` | No | Set `True` for ES module scripts |

## ES module scripts (js_module)

Set `js_module: bool = True` when the script needs the `type="module"`
attribute:

```python
# djdevx/providers/frameworks/frankenui/__init__.py
@register
class FrankenUIFramework(BaseFramework):
    name: str = "frankenui"
    display_name: str = "Franken UI"
    css_url = "https://cdn.jsdelivr.net/npm/franken-ui@1.0.3/dist/css/franken-ui.min.css"
    css_filename = "franken.css"
    js_url = "https://cdn.jsdelivr.net/npm/franken-ui@1.0.3/dist/js/franken-ui.min.js"
    js_filename = "franken.js"
    js_module: bool = True
```

## Lifecycle

`BaseFramework` handles everything through its hooks — no need to override
`add()` or `remove()`:

```
install:
  1. after_copy_templates()    # downloads CSS/JS, injects into _base.html

remove:
  1. before_pixi_remove()      # removes tags from _base.html
  2. _uninstall_framework()    # deletes CSS/JS from static/
```

Injection details:
- The CSS `<link>` tag is inserted before `</head>`, the JS `<script>` tag
  before `</body>`.
- Downloads fall back to a `/* placeholder */` file on network error (so
  installs never hard-fail offline).
- Uninstall removes the tags with a regex and unlinks the CSS/JS files.

## Full custom hooks

Frameworks that don't fit the CDN download model override the hooks entirely.
`starting_point_ui` is a framework that ships no CDN files — it writes
placeholder CSS/JS, edits the Tailwind `input.css`, and injects its script tag
into `_base.html`:

```python
# djdevx/providers/frameworks/starting_point_ui/__init__.py
@register
class StartingPointUIFramework(BaseFramework):
    name: str = "starting_point_ui"
    display_name: str = "Starting Point UI"

    @property
    def _css_path(self) -> Path:
        return self.structure.root / "tailwind" / "src" / "css" / "starting-point.css"

    @property
    def _js_path(self) -> Path:
        return self.structure.static_js_dir / "vendor" / "starting-point.js"

    @property
    def _input_css_path(self) -> Path:
        return self.structure.tailwind_input_css

    def after_copy_templates(self) -> None:
        self._css_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._css_path.exists():
            self._css_path.write_text("/* starting-point placeholder */\n")

        self._js_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._js_path.exists():
            self._js_path.write_text("/* starting-point js placeholder */\n")

        content = self._input_css_path.read_text()
        if '@import "./starting-point.css";' not in content:
            content = '@import "./starting-point.css";\n' + content
            self._input_css_path.write_text(content)

        path = self._base_template_path
        if path.exists():
            template = path.read_text()
            if "starting-point.js" not in template:
                tag = "<script src=\"{% static 'js/vendor/starting-point.js' %}\"></script>"
                template = template.replace("</body>", f"    {tag}\n  </body>")
                path.write_text(template)

    def before_pixi_remove(self) -> None:
        self._css_path.unlink(missing_ok=True)
        self._js_path.unlink(missing_ok=True)

        if self._input_css_path.exists():
            content = self._input_css_path.read_text()
            content = content.replace('@import "./starting-point.css";\n', "")
            self._input_css_path.write_text(content)

        path = self._base_template_path
        if path.exists():
            template = path.read_text()
            tag = "<script src=\"{% static 'js/vendor/starting-point.js' %}\"></script>"
            template = re.sub(r"\s*" + re.escape(tag) + r"\s*\n?", "", template)
            path.write_text(template)
```

The mutate / revert pairing (`after_copy_templates` / `before_pixi_remove`)
is the same convention used across installables — see
[Lifecycle Hooks](creating-an-installable.md#lifecycle-hooks).

## Framework templates

If the framework needs configuration files (e.g., `tailwind.config.js`):

```
djdevx/providers/frameworks/<name>/
├── __init__.py
└── templates/
    └── <filename>.j2
```

Templates render to the project root.

## Testing

```bash
ddx frameworks add bootstrap
ddx frameworks list                # verify check mark
ddx frameworks remove bootstrap
ddx frameworks list                # verify cross mark
```

See [Testing](creating-an-installable.md#testing) for the CLI integration
test pattern and golden-file fixtures.

## Related

- [Common Concepts](creating-an-installable.md) — shared pattern, variants, params, hooks, templates
- [Framework Architecture](framework-architecture.md) — BaseFramework details
- [Installable System](installable-system.md) — Shared infrastructure
- [Template System](template-system.md) — Jinja2 rendering conventions
