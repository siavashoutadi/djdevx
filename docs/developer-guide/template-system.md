# Template System

The template system powers both **project scaffolding** (generating a complete Django
project from scratch) and **per-package installation** (rendering settings snippets,
URL configs, and app files when a package is installed). It uses
[Jinja2](https://jinja.palletsprojects.com/) with a `FileSystemLoader` and is
organized into three layers:

| Layer | Class / Module | Responsibility |
|---|---|---|
| **Engine** | `TemplateManager` (`djdevx/utils/templates/manager.py`) | Jinja2 rendering, file copy, line-based cleanup |
| **Wrapper** | `DjangoProjectManager` (`djdevx/utils/django/project_manager.py`) | Project-aware delegation; hardcodes `dest_dir` to the Django project root |
| **Integration** | `BasePackage` (`djdevx/backend/django/packages/_base.py`) | Auto-routes templates per-package, collects CLI context via `install_params`, provides lifecycle hooks |

---

## TemplateManager (core engine)

**File:** `djdevx/utils/templates/manager.py`

```python
from pathlib import Path
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader

class TemplateManager:
    ...
```

### `render_template_string(template_str, template_context) -> str`

Render an arbitrary string through Jinja2. If the string contains no Jinja2 syntax
(`{{` or `{%`) it is returned unchanged as a fast-path optimisation.

```python
TemplateManager.render_template_string("Hello {{ name }}!", {"name": "World"})
# → "Hello World!"

TemplateManager.render_template_string("No templates here", {"name": "World"})
# → "No templates here"  (unchanged)
```

### `copy_templates(source_dir, dest_dir, template_context=None, exclude_files=None)`

Recursively walk `source_dir`, copying every file and directory to `dest_dir` with
Jinja2 processing applied to **both file/folder names and file contents**:

1. Each path component (directory name, filename) is rendered as a Jinja2 template
   so `{{backend_root}}/pyproject.toml.j2` becomes `backend/pyproject.toml.j2`.
2. Files ending in `.j2` have their **contents** rendered and the `.j2` suffix
   stripped. Non-`.j2` files are copied verbatim (but their filename is still
   rendered).
3. The output is always terminated with a single trailing newline.

```python
tm = TemplateManager()
tm.copy_templates(
    source_dir=Path("templates/my_package"),
    dest_dir=Path("/tmp/my_project"),
    template_context={"app_name": "blog", "debug": True},
    exclude_files=[Path("secret.txt")],
)
```

### `copy_template(source_file, dest_dir, template_context=None) -> Path`

Copy a **single** file with the same Jinja2 processing rules as `copy_templates`.
Returns the `Path` of the created file.

```python
tm = TemplateManager()
created = tm.copy_template(
    source_file=Path("templates/snippet.py.j2"),
    dest_dir=Path("/tmp/my_project/settings"),
    template_context={"app_name": "blog"},
)
# created → /tmp/my_project/settings/snippet.py
```

### `remove_lines_from_file(file_path, patterns_to_remove)`

Remove every line from a file that contains **any** of the given substrings.
Operates in-place via `fileinput`.

```python
TemplateManager.remove_lines_from_file(
    file_path=Path("static/css/input.css"),
    patterns_to_remove=["tailwind-ui"],
)
# Removes any line containing "tailwind-ui" from input.css
```

---

## DjangoProjectManager (project-aware wrapper)

**File:** `djdevx/utils/django/project_manager.py`

Wraps `TemplateManager` so callers don't need to specify `dest_dir` — it is always
the Django project root (the directory containing `pyproject.toml` inside the backend).

```python
pm = DjangoProjectManager()

# Delegates to TemplateManager.copy_templates with dest_dir=pm.project_path
pm.copy_templates(
    source_dir=Path("templates/startapp"),
    template_context={"application_name": "polls"},
)

# Delegates to TemplateManager.copy_template
pm.copy_template(
    source_file=Path("templates/settings_snippet.py"),
    dest_dir=pm.django_settings_path,
)
```

**Key path properties** on `DjangoProjectManager`:

| Property | Resolves to |
|---|---|
| `project_path` | `<backend_root>/` (parent of `pyproject.toml`) |
| `settings_path` | `<project_path>/settings/` |
| `django_settings_path` | `<settings_path>/django/` |
| `packages_settings_path` | `<settings_path>/packages/` |
| `urls_path` | `<project_path>/urls/` |
| `packages_urls_path` | `<urls_path>/packages/` |
| `base_template_path` | `<project_path>/templates/_base.html` |

---

## BasePackage integration

**File:** `djdevx/backend/django/packages/_base.py`

Every package subclass gets automatic template rendering through `_copy_templates()`:

```python
class MyPackage(BasePackage):
    name = "my-package"
    packages = ["my-package"]

    # (Optional) Override auto-derived paths
    template_path = "custom/path"    # relative to templates/django/
    settings_file = "custom_name.py" # output filename in settings/packages/
    url_file = "custom_url.py"       # output filename in urls/packages/
```

### Path auto-derivation

When `template_path`, `settings_file`, or `url_file` are not explicitly set they are
derived from the package file's location under `djdevx/backend/django/packages/`:

| Package file | `template_path` | `settings_file` | `url_file` |
|---|---|---|---|
| `packages/drf_spectacular.py` | `drf_spectacular` | `drf_spectacular.py` | `drf_spectacular.py` |
| `packages/django_storages/s3.py` | `django_storages/s3` | `django_storages_s3.py` | `django_storages_s3.py` |

### `_copy_templates(context)`

Called automatically during install. It resolves the template source directory:

```
djdevx/templates/django/<template_path>/
```

If that directory exists, every file inside is rendered with the given `context`
dict and written to the project root.

---

## Template directory layout

### Per-package templates (`templates/django/`)

Each package has a directory named after its `template_path`. Inside, files follow
conventional locations that mirror the project structure:

```
templates/django/
├── <template_path>/           # e.g. django_allauth/account
│   ├── settings/
│   │   └── packages/
│   │       └── <name>.py.j2  # → settings/packages/<name>.py
│   └── urls/
│       └── packages/
│           └── <name>.py.j2  # → urls/packages/<name>.py
├── startapp/                  # special: used by `ddx startapp`
│   ├── {{ application_name }}/
│   │   ├── views.py.j2
│   │   └── urls.py.j2
│   ├── settings/apps/
│   │   └── {{ application_name }}.py.j2
│   └── urls/apps/
│       └── {{ application_name }}.py.j2
└── pwa/                       # feature-level templates
    ├── pwa/
    ├── settings/apps/
    └── urls/apps/
```

Some packages have templates with **no** `.j2` extension (plain Python files that
are copied verbatim). These are used when the content is static and needs no
context variables.

### Project scaffolding (`templates/new/`)

Used by `ddx new backend django`:

```
templates/new/backend/django/
├── .devcontainer/
│   ├── devcontainer.json
│   ├── Dockerfile.j2
│   └── docker-compose.yaml
├── .djdevx/
│   └── config.toml.j2
├── .editorconfig
├── .gitignore.j2
├── prek.toml.j2
├── {{backend_root}}/
│   ├── .gitignore.j2
│   ├── .python-version.j2
│   ├── Dockerfile.j2
│   ├── pyproject.toml.j2
│   └── settings/django/
│       └── email.py.j2
```

---

## File extension convention

Templates use the `.j2` extension. On render:

- `.j2` is **stripped** from the filename: `urls.py.j2` → `urls.py`
- Non-`.j2` files are copied as-is: `docker-compose.yaml` → `docker-compose.yaml`

---

## Dynamic file and directory names

Directory and file names are rendered as Jinja2 strings before the file is created.
This allows context variables in paths:

```
templates/django/startapp/{{ application_name }}/views.py.j2
```

With context `{"application_name": "polls"}`, this produces:

```
polls/views.py
```

This works at every depth:

```
templates/new/backend/django/{{backend_root}}/settings/django/email.py.j2
# → backend/settings/django/email.py  (when backend_root="backend")
```

---

## Template context

Context variables are gathered from different sources depending on the code path:

### 1. `install_params` (declarative CLI options)

Declare `InstallParam` objects to have BasePackage auto-generate a Typer `install`
command with matching `--options`. Collected values are passed as Jinja2 context.

```python
from ._base import BasePackage, InstallParam

class MailgunPackage(BasePackage):
    name = "django-anymail Mailgun"
    packages = ["django-anymail[mailgun]<16"]

    install_params = [
        InstallParam(name="is_europe", type_=bool, default=False),
    ]
```

The template then uses `{{ is_europe }}`:

```jinja2
{%- if is_europe %}
"MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
{%- else %}
"MAILGUN_API_URL": "https://api.mailgun.net/v3",
{%- endif %}
```

#### InstallParam fields

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Key in template context dict and CLI `--<name>` option name |
| `type_` | `type` | Python type for the Typer option (default `str`) |
| `default` | `Any` | Default value when not supplied |
| `help` | `str` | Help text for `--help` |
| `prompt` | `Optional[str]` | If set, Typer prompts interactively |
| `show_if` | `Optional[str]` | Name of another param; only prompt if that param is `True` and the current value is empty |
| `message_before_prompt` | `Optional[str]` | Printed before a `show_if` conditional prompt |
| `hide_input` | `bool` | Hide terminal input (for passwords/tokens) |

#### Conditional prompts with `show_if`

```python
InstallParam(name="configure_facebook", type_=bool, default=False),
InstallParam(
    name="fb_app_id",
    show_if="configure_facebook",
    message_before_prompt="\nGet your App ID from: https://developers.facebook.com/apps/",
),
```

The `fb_app_id` prompt only fires when `configure_facebook=True` was entered and
`fb_app_id` is still empty.

### 2. Manual context (overridden `install()`)

When a package needs full control (e.g. computed defaults, validation, or
dependency-checking), it overrides `install()` and passes any dict:

```python
def install(self, enable_totp: bool = True, ...) -> None:
    ...
    self._copy_templates(context={
        "enable_totp": enable_totp,
        "enable_recovery_codes": enable_recovery_codes,
        "totp_period": totp_period,
        "totp_digits": totp_digits,
        ...
    })
```

### 3. Scaffolding context (hardcoded)

In `new/backend/django.py` the context is built from CLI parameters:

```python
data = {
    "project_name": project_name,
    "project_description": project_description,
    "python_version": python_version,
    "django_version": DJANGO_VERSION,
    "backend_root": backend_root,
}
template_manager.copy_templates(source_dir=source_dir, dest_dir=dest_dir, template_context=data)
```

---

## Install lifecycle and template hooks

```
before_uv_install()
    ↓
_uv_add_all()
    ↓
after_uv_install()
    ↓
before_copy_templates()     ← override to prepare the project
    ↓
_copy_templates(context)    ← renders & copies all templates
    ↓
after_copy_templates()      ← override to modify rendered files
    ↓
_write_package_tracking()
    ↓
_generate_secrets()
```

### `before_copy_templates()`

Use for pre-render setup (e.g., ensuring directories exist, adding packages to
the list that `install_params` collected earlier):

```python
class AllauthAccountPackage(BasePackage):
    def before_uv_install(self) -> None:
        if self._install_context.get("is_profanity_for_username_enabled", True):
            self.packages = list(self.packages) + ["better-profanity"]
```

### `after_copy_templates()`

Use for post-render modifications to the generated files, such as injecting
template tags into base templates:

```python
class DjangoSnakeoilPackage(BasePackage):
    def after_copy_templates(self) -> None:
        base = self.pm.base_template_path
        content = base.read_text()
        content = content.replace(
            "{% load static %}",
            "{% load static %}\n{% load snakeoil %}",
        )
        base.write_text(content)
```

---

## Jinja2 features used

All examples are taken from real package templates.

### Variable interpolation

```jinja2
META_SITE_PROTOCOL = "{{ site_protocol }}"
META_SITE_DOMAIN = "{{ site_domain }}"
```

### Conditionals

```jinja2
{%- if is_europe %}
"MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
{%- else %}
"MAILGUN_API_URL": "https://api.mailgun.net/v3",
{%- endif %}
```

### Boolean rendering with Python expressions

```jinja2
MFA_PASSKEY_LOGIN_ENABLED = {{ 'True' if passkey_login else 'False' }}
MFA_PASSKEY_SIGNUP_ENABLED = {{ 'True' if passkey_signup else 'False' }}
```

### Arithmetic

```jinja2
MFA_TRUST_COOKIE_AGE = {{ trust_cookie_age_days * 24 * 60 * 60 }}
```

### String methods

```jinja2
{%- if site_url.startswith('http://') or site_url.startswith('https://') %}
{"name": "twitter:domain", "content": "{{ site_url.split('://')[1].split('/')[0] }}"},
{%- endif %}
```

### Default filter

```jinja2
META_USE_OG_PROPERTIES = {{ use_og_properties|default(False) }}
```

### Whitespace control

Use `{%-` and `-%}` to trim leading/trailing whitespace and avoid blank lines in
generated output:

```jinja2
{% if site_name -%}
META_SITE_NAME = "{{ site_name }}"
{% endif -%}
```

---

## Complete examples

### Simple: `django_anymail/mailgun.py`

**Package** — `djdevx/backend/django/packages/django_anymail/mailgun.py`
```python
class MailgunPackage(BasePackage):
    name = "django-anymail Mailgun"
    packages = ["django-anymail[mailgun]<16"]

    install_params = [
        InstallParam(name="is_europe", type_=bool, default=False),
    ]
```

**Template** — `templates/django/django_anymail/mailgun/settings/packages/django_anymail_mailgun.py.j2`
```jinja2
{%- if is_europe %}
"MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
{%- else %}
"MAILGUN_API_URL": "https://api.mailgun.net/v3",
{%- endif %}
```

**Generated** — `settings/packages/django_anymail_mailgun.py`
```python
"MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
```

### Complex: `django_allauth/mfa.py`

**Package** — `djdevx/backend/django/packages/django_allauth/mfa.py`

Overrides `install()` to accept 14 typed parameters, validates a dependency
(allauth account must be installed first), and passes everything as template
context:

```python
class MfaPackage(BasePackage):
    name = "django-allauth MFA"
    packages = ["django-allauth[mfa]<66"]

    def install(
        self,
        enable_totp: bool = True,
        enable_recovery_codes: bool = True,
        enable_webauthn: bool = False,
        ...
    ) -> None:
        # Dependency check
        if not account_settings_path.exists():
            raise typer.Exit(...)

        self.before_uv_install()
        self._uv_add_all()
        self.after_uv_install()
        self.before_copy_templates()
        self._copy_templates(context={
            "enable_totp": enable_totp,
            "enable_recovery_codes": enable_recovery_codes,
            ...
        })
        self.after_copy_templates()
```

### Conditional prompts: `django_meta.py`

**Package** — `djdevx/backend/django/packages/django_meta.py`

Shows `show_if` gating — Facebook/Twitter sub-options are only prompted when the
user opts in:

```python
install_params = [
    InstallParam(name="configure_facebook", type_=bool, default=False),
    InstallParam(name="fb_app_id", show_if="configure_facebook",
                 message_before_prompt="\nGet your App ID from: https://developers.facebook.com/apps/"),
    InstallParam(name="configure_twitter", type_=bool, default=False),
    InstallParam(name="twitter_site", show_if="configure_twitter"),
    ...
]
```

**Template** — `templates/django/django_meta/settings/packages/django_meta.py.j2`
```jinja2
{% if configure_facebook -%}
{% if fb_app_id -%}
META_FB_APPID = "{{ fb_app_id }}"
{% endif -%}
{% endif -%}
```

### Project scaffolding: `new/backend/django.py`

Uses `TemplateManager` directly (no `BasePackage`) to render a full Django project:

```python
template_manager = TemplateManager()
template_manager.copy_templates(
    source_dir=Path("templates/new/backend/django"),
    dest_dir=project_directory.absolute(),
    template_context={
        "project_name": "my-project",
        "python_version": "3.14",
        "django_version": "6.0",
        "backend_root": "backend",
    },
)
```

---

## Testing

Template rendering is verified through integration tests in `tests/backend/django/`:

- **`test_basepackage.py`** — Tests `PathDeriver` (path derivation logic),
  `install_params` signature injection, lifecycle hook ordering, `show_if`
  conditional prompts, and package tracking.

- **`packages/test_django_anymail.py`** — End-to-end tests that:
  1. Create a fresh Django backend via `create_test_django_backend()`
  2. Run the install CLI command
  3. Verify the rendered settings file exists
  4. Compare actual output against expected content in `tests/backend/django/packages/data/`
  5. Run the remove command and verify cleanup

- **`new/backend/test_django.py`** — Tests the full `ddx new backend django`
  scaffolding command, verifying all expected files are created with correct content.

To add a new package test: create a test that invokes your package's install
command and assert on the rendered file content. The test helper
`create_test_django_backend()` in `tests/test_helpers.py` sets up a clean project
for each test case.

---

## Creating a new package with templates

1. Create your package file at `djdevx/backend/django/packages/<name>.py`
   (or `packages/<group>/<name>.py` for sub-packages).

2. Create a template directory at
   `djdevx/templates/django/<template_path>/` (where `<template_path>`
   matches the auto-derived path or your explicit `template_path` override).

3. Add template files with `.j2` extension. Use `settings/packages/`
   and `urls/packages/` subdirectories to mirror the project structure.

4. Declare `install_params` for CLI-collected context, or override `install()`
   for full control.

5. Implement `before_copy_templates()` / `after_copy_templates()` hooks if
   the package needs pre- or post-render logic.

## Related

- [Package Architecture](package-architecture.md) — How packages use templates
- [Creating a Package](creating-a-package.md) — Step-by-step guide
