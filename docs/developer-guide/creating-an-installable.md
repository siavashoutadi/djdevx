# Common Concepts

Every installable — package, feature, framework, database, or cache — follows
the same core pattern. This page explains the shared pattern and the
cross-cutting concepts: variants, install parameters, secret generators,
dependencies, lifecycle hooks, templates, and testing.

For type-specific guides, see:

- [Add a Package](adding-a-package.md) — third-party Django packages, variants, params, secrets
- [Add a Feature](adding-a-feature.md) — higher-level components, dependencies on packages
- [Add a Framework](adding-a-framework.md) — CSS/JS frameworks injected into `_base.html`
- [Add a Database](adding-a-database.md) — database providers with Docker Compose
- [Add a Cache](adding-a-cache.md) — cache providers with Docker Compose

## Table of Contents

1. [Common Pattern (All Types)](#common-pattern-all-types)
2. [Working with Variants](#working-with-variants)
3. [Install Parameters](#install-parameters)
4. [Secret Generators](#secret-generators)
5. [Dependencies (needs)](#dependencies-needs)
6. [Lifecycle Hooks](#lifecycle-hooks)
7. [Templates](#templates)
8. [Testing](#testing)

---

## Common Pattern (All Types)

Every installable follows this structure:

```
djdevx/<category>/<name>/
├── __init__.py            # @register decorated class
└── templates/             # Jinja2 templates (optional)
    └── settings/
        └── packages/
            └── <name>.py.j2
```

### Base class mapping

| Installable type | Base class | `section` | Directory |
|---|---|---|---|
| Package | `BasePackage` | `"packages"` | `djdevx/packages/<name>/` |
| Feature | `BaseFeature` | `"features"` | `djdevx/features/<name>/` |
| Framework | `BaseFramework` | `"frameworks"` | `djdevx/frameworks/<name>/` |
| Database | `BaseDatabase` | `"database"` | `djdevx/database/<name>/` |
| Cache | `BaseCache` | `"cache"` | `djdevx/cache/<name>/` |

### Scaffold the module

```python
# djdevx/packages/<name>/__init__.py
from __future__ import annotations

from .._base import BasePackage
from .._registry import register
from djdevx.utils.types.pixi_types import PixiPackageSpec


@register
class MyItem(BasePackage):
    name: str = "my-item"
    display_name: str = "My Item"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-my-item")]
```

Key rules:
- The class **must** use `@register` from the category's `_registry.py`
- `name` is the unique identifier (hyphens preferred, underscores normalized)
- `pixi_packages` lists dependencies installed via `pixi add`
- No manual registration anywhere — `discover_and_register()` auto-imports it

### Class attributes reference

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Unique identifier (underscores → hyphens) |
| `display_name` | `str` | Yes | Human-readable name for CLI output |
| `description` | `str` | No | Longer description |
| `pixi_packages` | `list[PixiPackageSpec]` | No | Dependencies via pixi (set `pixi_feature="dev"` for dev-only) |
| `conditional_packages` | `list[ConditionalPackage]` | No | Pixi packages installed only when their `when(installable)` condition holds |
| `needs` | `list[InstallableRef]` | No | Other installables that must be installed first |
| `template_path` | `str` | No | Override auto-derived template directory |
| `install_params` | `list[InstallParam]` | No | Parameters collected at install time |
| `secret_generators` | `dict[str, Callable]` | No | Maps field names to generator callables |
| `files_to_remove` | `list[str]` | No | Extra files to delete on uninstall |
| `folders_to_remove` | `list[str]` | No | Extra directories to delete on uninstall |
| `restore_on_remove` | `dict[str, str]` | No | Template overrides (project_rel → template_rel) |
| `exclusive_variants` | `bool` | No | If `True`, user picks exactly one variant |
| `variants` | `dict[str, Variant]` | No | Named variants (backends, providers, etc.) |

### PixiPackageSpec

`pixi_packages` entries accept three fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Package spec — may include a version constraint (e.g. `"whitenoise<7"`) or extras (e.g. `"django-storages[s3,azure,google]"`) |
| `kind` | `"conda" \| "pypi"` | Source channel. Defaults to `conda`; use `"pypi"` for PyPI-only packages |
| `pixi_feature` | `str \| None` | Install under a pixi feature. Set `"dev"` for dev-only dependencies |

Real-world examples:

```python
# Version constraint (conda)
PixiPackageSpec("whitenoise<7")

# PyPI-only package
PixiPackageSpec("django-tailwind-cli", kind="pypi")

# Dev-only dependency
PixiPackageSpec("django-debug-toolbar", pixi_feature="dev")

# PyPI extras baked into the name
PixiPackageSpec("django-storages[s3,azure,google]", kind="pypi")

# Multiple packages on one installable
pixi_packages: list[PixiPackageSpec] = [
    PixiPackageSpec("django-health-check"),
    PixiPackageSpec("psutil", kind="pypi"),
]
```

### ConditionalPackage

Each entry in `conditional_packages` wraps **one** `PixiPackageSpec` with its
own `when` callable:

| Field | Type | Description |
|-------|------|-------------|
| `package` | `PixiPackageSpec` | The dependency to install when the condition holds |
| `when` | `Callable[..., bool]` | Called with the installable instance as first argument; `True` includes the package |

The condition runs during both add and remove. Pass an unbound method
reference to read instance state, or a lambda with a single parameter:

```python
from djdevx.utils.installable import ConditionalPackage


class ChannelsPackage(BasePackage):
    name: str = "channels"
    display_name: str = "Channels"
    use_redis: bool = False

    def _needs_redis(self) -> bool:
        return self.use_redis

    conditional_packages: list[ConditionalPackage] = [
        ConditionalPackage(
            package=PixiPackageSpec("channels-redis", kind="pypi"),
            when=_needs_redis,
        ),
        ConditionalPackage(
            package=PixiPackageSpec("daphne", kind="pypi"),
            when=lambda self: self.use_daphne,
        ),
    ]
```

Variants can carry their own `conditional_packages` too — their conditions
receive the parent installable instance.

---

## Working with Variants

Variants come in two modes, controlled by `exclusive_variants`:

### Exclusive variants (`exclusive_variants=True`)

User picks exactly one variant. Used when variants are mutually exclusive
backends (storage: S3 vs Azure, email: SES vs Brevo).

```python
exclusive_variants: bool = True
variants: dict[str, Variant] = {
    "s3": Variant(name="s3", display_name="Amazon S3", template_path="s3"),
    "azure": Variant(name="azure", display_name="Azure", template_path="azure"),
}
```

### Additive variants (`exclusive_variants=False`)

User can install multiple variants. Used for optional sub-features (allauth:
account + mfa + oidc).

```python
exclusive_variants: bool = False
variants: dict[str, Variant] = {
    "account": Variant(name="account", display_name="Account", required=True, ...),
    "mfa": Variant(name="mfa", display_name="MFA", ...),
}
```

### Variant attributes

`Variant` inherits every installable config attribute, so variants may carry
their own `pixi_packages`, `template_path`, `install_params`,
`secret_generators`, `needs`, `files_to_remove`, `folders_to_remove`, and
`restore_on_remove` — plus:

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier |
| `display_name` | `str` | Human-readable name |
| `required` | `bool` | Auto-installed when parent is added |
| `pixi_packages` | `list[PixiPackageSpec]` | Variant-specific dependencies |
| `conditional_packages` | `list[ConditionalPackage]` | Variant-specific gated dependencies (conditions receive the parent installable) |
| `template_path` | `str` | Override template directory |
| `install_params` | `list[InstallParam]` | Variant-specific install parameters |
| `secret_generators` | `dict[str, Callable]` | Variant-specific secret generators |
| `files_to_remove` | `list[str]` | Files to delete on uninstall |
| `folders_to_remove` | `list[str]` | Folders to delete on uninstall |
| `restore_on_remove` | `dict[str, str]` | Template overrides |

### Variant templates

Variant templates go in subdirectories named after the variant's
`template_path`:

```
djdevx/packages/<name>/templates/
├── <variant1_template_path>/
│   └── settings/packages/<name>_<variant1>.py
└── <variant2_template_path>/
    └── settings/packages/<name>_<variant2>.py
```

### CLI variant selection

```bash
# With -p/--provider flag (non-interactive)
ddx packages add django-storages -p s3
ddx packages remove django-storages -p s3

# Interactive — prompts for variant selection
ddx packages add django-storages
```

---

## Install Parameters

`InstallParam` declares CLI parameters collected at install time and passed
to Jinja2 templates as context variables.

### Simple params

```python
install_params: list[InstallParam] = [
    InstallParam(name="site_name", prompt="Site name"),
    InstallParam(name="site_protocol", default="https", prompt="Site protocol"),
]
```

### Boolean params

```python
InstallParam(name="enable_logging", type_=bool, default=True,
             prompt="Enable debug logging?"),
```

### Conditional prompts (show_if)

```python
InstallParam(name="configure_facebook", type_=bool, default=False,
             prompt="Configure Facebook?"),
InstallParam(
    name="fb_app_id",
    show_if="configure_facebook",
    message_before_prompt="\nGet your App ID from: https://developers.facebook.com/apps/",
),
```

The `fb_app_id` prompt only fires when `configure_facebook=True` and
`fb_app_id` is still empty.

### Hidden input (passwords)

```python
InstallParam(name="api_key", hide_input=True, prompt="Enter your API key"),
```

### InstallParam reference

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Key in template context and CLI prompt |
| `type_` | `type` | Python type (default `str`) |
| `default` | `Any` | Default value |
| `help` | `str` | Help text for `--help` |
| `prompt` | `Optional[str]` | If set, prompts user interactively |
| `show_if` | `Optional[str]` | Only prompt if this other param is truthy |
| `message_before_prompt` | `Optional[str]` | Printed before a conditional prompt |
| `hide_input` | `bool` | Hide terminal input (for passwords/tokens) |

### Template usage

```jinja2
META_SITE_NAME = "{{ site_name }}"
META_SITE_PROTOCOL = "{{ site_protocol }}"

{% if configure_facebook %}
META_FB_APPID = "{{ fb_app_id }}"
{% endif %}
```

### Install params on variants

Install params can also be placed on individual variants:

```python
"account": Variant(
    name="account",
    template_path="account",
    install_params=[
        InstallParam(name="email_subject_prefix", prompt="Subject prefix"),
    ],
),
```

---

## Secret Generators

For settings templates with `SecretStr` fields that should be auto-generated:

```python
from djdevx.utils.generators import generate_random_password, generate_rsa_private_key

class MyPackage(BasePackage):
    secret_generators: dict[str, Callable] = {
        "api_key": generate_random_password,
        "idp_oidc_private_key": generate_rsa_private_key,
    }
```

### Available generators

| Generator | Description |
|-----------|-------------|
| `generate_random_password(length=64)` | Cryptographically random alphanumeric string |
| `generate_rsa_private_key()` | 2048-bit RSA private key (PEM format) |

### How it works

When `secrets init dev` runs, the `SettingCollector` discovers `SecretStr`
fields. For fields with a registered generator, if no secret file exists yet,
the generator is called and the result written to `.secrets/<field_name>`.

### Secret generators on variants

```python
"oidc_provider": Variant(
    name="oidc_provider",
    secret_generators={
        "idp_oidc_private_key": generate_rsa_private_key,
    },
),
```

---

## Dependencies (needs)

Use `needs` to declare dependencies on other installables. Dependencies are
automatically installed before the target.

```python
from djdevx.utils.installable.types import InstallableRef
from djdevx.utils.installable.types import PACKAGE, FEATURE

class SSOFeature(BaseFeature):
    name: str = "sso"
    display_name: str = "Single Sign-On"
    needs: list[InstallableRef] = [
        InstallableRef("django-allauth", PACKAGE),
        InstallableRef("pwa", FEATURE),
    ]
```

### InstallableKind references

| Kind constant | Refers to |
|---|---|
| `PACKAGE` | Packages |
| `FEATURE` | Features |
| `FRAMEWORK` | Frameworks |
| `DATABASE` | Databases |
| `CACHE` | Caches |

Cross-category dependencies work — a feature can depend on a package, a
database can depend on a package, etc. See [Add a Feature](adding-a-feature.md)
for a real cross-category example (`sso` → `django-allauth`).

---

## Lifecycle Hooks

Override these in your installable for custom behavior:

| Hook | Timing | Common uses |
|------|--------|-------------|
| `before_pixi_install()` | Before `pixi add` | Pre-install checks |
| `after_pixi_install()` | After `pixi add` | Docker Compose setup, file prep |
| `before_copy_templates()` | Before Jinja2 rendering | Create directories, prepare state |
| `after_copy_templates()` | After Jinja2 rendering | CSS/JS download, icon generation, base template injection |
| `before_pixi_remove()` | Before `pixi remove` | Docker Compose cleanup, tag removal from templates |
| `after_pixi_remove()` | After `pixi remove` | Extra cleanup |

The most common convention is a **mutate / revert pair**:

- `after_copy_templates()` mutates generated files (e.g. injects tags into
  `_base.html`, edits `users/models.py`).
- `before_pixi_remove()` reverses the mutation (regex/string removal).

This is how `django-guardian`, `django-htmx`, `django-snakeoil`,
`django-tailwind-cli`, the `pwa` feature, and the frameworks all behave.

### Hook examples

```python
# after_pixi_install — add Docker services
def after_pixi_install(self) -> None:
    compose = DockerComposeManager(self.structure.root)
    compose.add_service(MY_SERVICE, MY_VOLUMES)

# after_copy_templates — download files, modify rendered templates
def after_copy_templates(self) -> None:
    # Download CSS
    dest = self.structure.static_css_dir / "vendor" / self.css_filename
    urllib.request.urlretrieve(self.css_url, dest)

    # Modify rendered template
    base = self.structure.base_template
    content = base.read_text()
    content = content.replace("</head>", f'  <link ...>\n</head>')
    base.write_text(content)

# before_pixi_remove — clean up files that cleanup_files won't touch
def before_pixi_remove(self) -> None:
    self.structure.django_settings_dir.joinpath("extra_generated.py").unlink(missing_ok=True)
```

### Accessing install context in hooks

Install-time parameter values are available via `self._install_context`:

```python
def after_copy_templates(self) -> None:
    icon_path = self._install_context.get("icon_path", "")
    if icon_path:
        self._generate_icons(icon_path)
```

`before_copy_templates()` can also **enrich** the context — derive new keys
that templates and later hooks can read (see
[Enriching the install context](adding-a-feature.md#enriching-the-install-context)).

### Tracking generated files

`cleanup_files` only deletes files that `copy_templates` created (it mirrors
the template scan to compute exactly what was written). Files generated
**programmatically** in hooks are not tracked — list them in
`files_to_remove` / `folders_to_remove`:

```python
files_to_remove: list[str] = [
    "pwa/templates/manifest.json",
    "templates/apple_splash.html",
]
folders_to_remove: list[str] = [
    "static/images/icons/android",
    "static/images/icons/ios",
]
```

---

## Templates

Templates use Jinja2 with a `.j2` extension (stripped on render). Directory
and file names can contain Jinja2 expressions for dynamic paths.

### Template location

Each installable's templates live at `{module_dir}/templates/`. The
`scaffold.py` module handles resolution and rendering automatically.

### File extension convention

- `.j2` files — rendered through Jinja2, `.j2` stripped from output filename
- Non-`.j2` files — copied verbatim

### Template context

Context comes from `install_params` collected at install time (via the
orchestrator). Values are available as Jinja2 variables:

```jinja2
{% if enable_login_by_code %}
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
{% endif %}

META_SITE_NAME = "{{ site_name }}"
```

### Dynamic file names

Directory and file names are rendered as Jinja2 strings before creation:

```
templates/{{ application_name }}/views.py.j2  →  polls/views.py
```

### Template conventions by type

| Installable type | Template location | Project destination |
|---|---|---|
| Package | `packages/<name>/templates/settings/packages/` | `settings/packages/<name>.py` |
| Package URLs | `packages/<name>/templates/urls/packages/` | `urls/packages/<name>.py` |
| Feature | `features/<name>/templates/` | Project root |
| Framework | `frameworks/<name>/templates/` | Project root |
| Database | `database/<name>/templates/settings/django/` | `settings/django/database.py` |
| Cache | `cache/<name>/templates/settings/django/` | `settings/django/caches.py` |

### Settings templates and pydantic-settings

For packages that need configuration management, create settings templates
that define `AppBaseSettings` subclasses. See
[Pydantic Settings](pydantic-settings.md) for the full reference.

---

## Testing

Test files mirror the source directory structure:

| Source module | Test file |
|---|---|
| `djdevx/packages/<name>/` | `tests/packages/test_<name>.py` |

### CLI Integration Test Pattern

```python
import os
from pathlib import Path
from typer.testing import CliRunner
from djdevx.main import app
from tests.test_helpers import create_test_django_backend

runner = CliRunner()
DATA_DIR = Path(__file__).parent / "data" / "<name>"


def test_install_and_remove(temp_dir):
    project_dir = create_test_django_backend(temp_dir, runner)
    os.chdir(temp_dir)

    # Install
    result = runner.invoke(app, ["packages", "add", "<name>"])
    assert result.exit_code == 0

    # Verify files
    settings_file = project_dir / "settings" / "packages" / "<name>.py"
    assert settings_file.exists()
    assert settings_file.read_text() == (
        DATA_DIR / "settings" / "packages" / "<name>.py"
    ).read_text()

    # Remove
    result = runner.invoke(app, ["packages", "remove", "<name>"])
    assert result.exit_code == 0
    assert not settings_file.exists()
```

### Data Fixtures (Golden Files)

Store expected output in `tests/packages/data/<name>/` mirroring the
generated structure:

```
tests/packages/data/<name>/
├── .djdevx/packages/<name>/config.toml
└── settings/packages/<name>.py
```

See [Testing](testing.md) for full details on test patterns.

---

## Related

- [Installable System](installable-system.md) — Full architecture reference
- [Add a Package](adding-a-package.md) — Package-specific how-to
- [Add a Feature](adding-a-feature.md) — Feature-specific how-to
- [Add a Framework](adding-a-framework.md) — Framework-specific how-to
- [Add a Database](adding-a-database.md) — Database-specific how-to
- [Add a Cache](adding-a-cache.md) — Cache-specific how-to
- [Package Architecture](package-architecture.md) — BasePackage details
- [Feature Architecture](feature-architecture.md) — BaseFeature details
- [Framework Architecture](framework-architecture.md) — BaseFramework details
- [Database Architecture](database-architecture.md) — BaseDatabase details
- [Cache Architecture](cache-architecture.md) — BaseCache details
- [Template System](template-system.md) — Jinja2 rendering
- [Pydantic Settings](pydantic-settings.md) — Settings and secrets
- [Testing](testing.md) — Test patterns
