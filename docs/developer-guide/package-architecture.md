# Package Architecture

## BasePackage

Every installable Django package inherits from `BasePackage`
(`djdevx/backend/django/packages/_base.py`):

```python
from djdevx.backend.django.packages._base import BasePackage

class MyPackage(BasePackage):
    name = "my-package"
    packages = ["django-my-package"]
    dev_packages = []
```

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique package identifier (used in CLI commands and messages) |
| `packages` | `list[str]` | PyPI package names to install via `uv add` |
| `dev_packages` | `list[str]` | Dev-only PyPI dependencies added via `uv add --group dev` |
| `required_dependencies` | `list[str]` | Other djdevx package names that must be installed first; install exits with an error and hint if missing |
| `install_params` | `list[InstallParam]` | Parameters to collect at install time — auto-generates Typer CLI options and Jinja2 template context |
| `secret_generators` | `dict[str, Callable]` | Maps pydantic `SecretStr` field names to generator callables; called at end of install, idempotent |
| `files_to_remove` | `list[str]` | Project-relative file paths to delete on uninstall |
| `folders_to_remove` | `list[str]` | Project-relative directory paths to recursively delete on uninstall |
| `settings_file` | `Optional[str]` | Override auto-derived settings filename (see Path Auto-Derivation) |
| `url_file` | `Optional[str]` | Override auto-derived URL filename (see Path Auto-Derivation) |
| `template_path` | `Optional[str]` | Override auto-derived template directory (see Path Auto-Derivation) |

`required_dependencies` example — `djangochannelsrestframework` requires `channels` to be installed first:

```python
class DjangoChannelsRestFrameworkPackage(BasePackage):
    name = "djangochannelsrestframework"
    packages = ["djangochannelsrestframework<2"]
    required_dependencies = ["channels"]
```

This checks that the `channels` PyPI package exists in `pyproject.toml`.
If missing, the CLI prints:

```
'channels' package is required for 'djangochannelsrestframework'.
Please install that first.

> ddx backend django packages channels install
```

> **Note:** `required_dependencies` checks PyPI package names in
> `pyproject.toml`. For sub-package dependencies (e.g., MFA requiring
> account to be installed first), use a manual settings-file check in
> your overridden `install()` — see `django_allauth/mfa.py` for an
> example.

### Path Auto-Derivation

`PathDeriver` (`_base.py:22`) automatically computes `settings_file`,
`url_file`, and `template_path` from the package module's location relative
to `packages/`. This means most packages never need to set these explicitly.

| Package location | `settings_file` | `url_file` | `template_path` |
|---|---|---|---|
| `packages/whitenoise.py` | `whitenoise.py` | `whitenoise.py` | `whitenoise` |
| `packages/django_allauth/account.py` | `django_allauth_account.py` | `django_allauth_account.py` | `django_allauth/account` |
| `packages/django_storages/s3.py` | `django_storages_s3.py` | `django_storages_s3.py` | `django_storages/s3` |

- **Root packages** (`packages/<name>.py`) → `settings_file: <name>.py`, `template_path: <name>`.
- **Sub-packages** (`packages/<dir>/<name>.py`) → `settings_file: <dir>_<name>.py`, `template_path: <dir>/<name>`.

Override by setting `settings_file`, `url_file`, or `template_path` on the
class — only needed when the derived name would conflict with another
package.

### Lifecycle Hooks

Packages can override these methods to customize behavior:

| Hook | Timing |
|------|--------|
| `before_uv_install()` | Before running `uv add` |
| `after_uv_install()` | After running `uv add` |
| `before_copy_templates()` | Before copying template files |
| `after_copy_templates()` | After copying template files |
| `before_uv_remove()` | Before running `uv remove` |
| `after_uv_remove()` | After running `uv remove` |

Hooks can access install-time parameter values via `self._install_context`.
This is useful for conditional logic in `before_uv_install()`:

```python
class AllauthAccountPackage(BasePackage):
    install_params = [
        InstallParam(name="is_profanity_for_username_enabled", type_=bool, default=True, prompt="Enable profanity filter for username"),
    ]

    def before_uv_install(self) -> None:
        if self._install_context.get("is_profanity_for_username_enabled", True):
            self.packages = list(self.packages) + ["better-profanity"]
```

### Full install() / remove() Override

When the auto-generated `install` (driven by `InstallParam` list) is not
flexible enough, override `install()` completely with custom Typer parameters.
This is useful for:

- Parameters with `min`/`max` constraints, `choices`, or `hidden` flags
- Complex validation across parameters
- Conditional logic that goes beyond `show_if`

Example from `django_allauth/mfa.py`:

```python
from typing_extensions import Annotated

class MfaPackage(BasePackage):
    name = "django-allauth MFA"
    packages = ["django-allauth[mfa]<66"]

    def install(
        self,
        enable_totp: Annotated[bool, typer.Option(prompt="Enable TOTP authentication")] = True,
        enable_webauthn: Annotated[bool, typer.Option(prompt="Enable WebAuthn/passkeys")] = False,
        totp_period: Annotated[int, typer.Option(min=15, max=300)] = 30,
        totp_digits: Annotated[int, typer.Option(min=6, max=8)] = 6,
    ) -> None:
        self.before_uv_install()
        self._uv_add_all()
        self.after_uv_install()
        self.before_copy_templates()
        self._copy_templates(context={...})
        self.after_copy_templates()
```

When `install()` is fully overridden, you must call the lifecycle hooks
(`before_uv_install`, `_uv_add_all`, `_copy_templates`, etc.) yourself.

The `remove()` method can also be overridden — for example, to skip removing
shared dependencies:

```python
def remove(self) -> None:
    self.before_uv_remove()
    self._cleanup_files()     # remove config files
    # Don't call _uv_remove_all() — parent package still needs django-allauth
    shutil.rmtree(self.pm.project_path / "authentication", ignore_errors=True)
```

### Settings & Secrets

Package settings are defined in pydantic `AppBaseSettings` subclasses within
settings templates, not inline in the package class. See
[Pydantic Settings Architecture](pydantic-settings.md) for the full
resolution chain.

For `SecretStr` fields that should be auto-generated at install time, use
`secret_generators`:

```python
from djdevx.utils.generators import generate_random_password

class MyPackage(BasePackage):
    secret_generators = {
        "api_key": generate_random_password,
    }
```

Available generators (in `djdevx/utils/generators/`):

| Generator | Description |
|-----------|-------------|
| `generate_random_password(length=64)` | Cryptographically random alphanumeric string |
| `generate_rsa_private_key()` | 2048-bit RSA private key (PEM format) |

Generators are pure functions. They run at the end of `install()`, writing
output to `.secrets/<field_name>`. See
[Auto-Generated Secrets](../user-guide/managing-settings.md#auto-generated-secrets).

### Template Directory

Package templates live under `djdevx/templates/django/<template_path>/` where
`<template_path>` is auto-derived from the module location (see
Path Auto-Derivation above). See [Template System](template-system.md) for
details on rendering.

Key conventions:
- **`.j2` extension** — files ending in `.j2` are rendered through Jinja2 and
  the `.j2` suffix is stripped from the output filename. Non-`.j2` files are
  copied as-is.
- **Dynamic filenames** — both file and directory names can contain Jinja2
  expressions, e.g. `{{ package_name }}/__init__.py.j2`.
- **Template context** — includes all `install_params` values, plus the
  project name, project directory, CSS framework, and other scaffolding
  metadata.

Typical template directory structure:

```
templates/django/<template_path>/
├── settings/
│   └── packages/
│       └── <settings_file>.j2     # Rendered → settings/packages/<name>.py
└── urls/
    └── packages/
        └── <url_file>.j2           # Rendered → urls/packages/<name>.py
```

If the template directory does not exist, template copying is silently
skipped (templates are optional — some packages only need `uv add`).

### Package Tracking

Each installed package is recorded under `.djdevx/backend/django/packages/`:

```
.djdevx/
└── backend/
    └── django/
        └── packages/
            └── whitenoise/             # Matches template_path
                └── config.toml         # [package] name = "whitenoise"
```

The `PackageTracker` class (`utils/djdevx_config/backend/package_tracker.py`)
manages these records. Installing a package creates its folder + config.toml;
removing it deletes the entire folder. The `ddx backend django list` command
reads these records to show installed packages.

## Sub-Package Groups

Packages with multiple backends or providers (like `django-storages`,
`django-anymail`, `django-allauth`) use a directory with an `__init__.py`
that aggregates sub-packages:

```
django_storages/
├── __init__.py    # Creates parent typer, adds s3/azure/google
├── s3.py          # BasePackage subclass
├── azure.py       # BasePackage subclass
└── google.py      # BasePackage subclass
```

The parent `__init__.py` follows this pattern:

```python
import typer
from .s3 import app as s3_app
from .azure import app as azure_app
from .google import app as google_app

app = typer.Typer(no_args_is_help=True)
app.add_typer(s3_app, name="s3", help="Manage django-storages with S3 backend")
app.add_typer(azure_app, name="azure", help="Manage django-storages with Azure backend")
```

Each sub-package is a normal `BasePackage` subclass — the path derivation
handles the nested location automatically (see Path Auto-Derivation table).

Sub-packages are registered by importing the parent group's `app` in
`packages/__init__.py`:

```python
from .django_storages import app as storages

app.add_typer(storages, name="django-storages", help="Manage django-storages package")
```

This produces CLI commands like:
```
ddx backend django packages django-storages s3 install
ddx backend django packages django-storages azure remove
```

## Registration

All packages (flat and group) are registered in
`djdevx/backend/django/packages/__init__.py` by importing their `app` and
adding it to the central `packages` Typer app:

```python
from .whitenoise import app as whitenoise

app = typer.Typer(no_args_is_help=True)
app.add_typer(whitenoise, name="whitenoise", help="Manage whitenoise package")
```

Each package module exposes a module-level singleton:

```python
_pkg = WhitenoisePackage(__file__)
app = _pkg.app
```

The `app` is a `typer.Typer()` instance that registers `install` and `remove`
commands for that package. The CLI exposes them under
`ddx backend django packages <name> [install|remove]`.

### CLI Command Reference

For every registered package, the CLI generates:

```
ddx backend django packages <name> install   — Install and configure <name>
ddx backend django packages <name> remove    — Remove <name> configuration
```

If the package declares `install_params`, each becomes a `--<option>` on the
install command:
```
ddx backend django packages my-package install --api-version v2 --enable-webhook
```

For sub-package groups, the nesting is preserved:
```
ddx backend django packages django-storages s3 install
ddx backend django packages django-allauth mfa install --enable-totp --totp-period 30
```

## Creating a Package

To add a new Django package to djdevx, create a subclass of `BasePackage`,
define its dependencies, create Jinja2 templates, and register it in the
CLI tree. The [Creating a Package](creating-a-package.md) step-by-step guide
walks through the entire process with examples.

## Related

- [Creating a Package](creating-a-package.md) -- Step-by-step guide for
  adding a new Django package to djdevx
- [Template System](template-system.md) -- Jinja2 rendering and directory
  conventions
- [Pydantic Settings Architecture](pydantic-settings.md) -- Settings
  resolution chain and SettingCollector
- [URL Architecture](url-architecture.md) -- URL auto-registration
