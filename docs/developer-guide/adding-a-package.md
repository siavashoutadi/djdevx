# Adding a Package

Step-by-step guide to adding a new Django package to djdevx. Packages are the
most common installable type — they install a third-party Django package with
optional variants, install-time parameters, and secret generation.

This page focuses on package-specific concerns. Shared concepts (variants,
install params, secrets, hooks, templates, testing) live in
[Common Concepts](creating-an-installable.md).

## Table of Contents

1. [Minimal package](#minimal-package)
2. [pixi_packages edge cases](#pixi_packages-edge-cases)
3. [Install params](#install-params)
4. [Exclusive variants](#exclusive-variants)
5. [Additive variants](#additive-variants)
6. [Secret generators](#secret-generators)
7. [Custom pre/post hooks](#custom-prepost-hooks)
8. [Reverting from the new template (restore_on_remove)](#reverting-from-the-new-template-restore_on_remove)
9. [Package templates directory](#package-templates-directory)
10. [Testing](#testing)

---

## Minimal package

```python
# djdevx/packages/whitenoise/__init__.py
from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from .._registry import register


@register
class WhitenoisePackage(BasePackage):
    name: str = "whitenoise"
    display_name: str = "Whitenoise"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("whitenoise<7")]
```

That's it. No `install()` override needed — the standard lifecycle handles
template copying and tracking. Most packages in `djdevx/packages/` are this
simple (`django-csp`, `django-filter`, `heroicons`, `django-simple-history`,
`drf-spectacular`, ...).

## pixi_packages edge cases

The `name` field of `PixiPackageSpec` is a full pixi package spec, so it can
carry constraints, extras, or even a wheel URL. The other two fields control
the source channel and pixi feature.

```python
# PyPI-only package
PixiPackageSpec("django-tailwind-cli", kind="pypi")

# Dev-only dependency (installed under the "dev" pixi feature)
PixiPackageSpec("django-debug-toolbar", pixi_feature="dev")

# Version constraint
PixiPackageSpec("django-allauth<66")

# PyPI extras baked into the name
PixiPackageSpec("django-storages[s3,azure,google]", kind="pypi")

# Multiple dependencies on one installable
pixi_packages: list[PixiPackageSpec] = [
    PixiPackageSpec("django-health-check"),
    PixiPackageSpec("psutil", kind="pypi"),
]
```

A wheel URL can even be used as the package name:

```python
PixiPackageSpec(
    "django-sp-admin @ https://github.com/siavashoutadi/.../django_sp_admin-0.1.0-py3-none-any.whl",
    kind="pypi",
)
```

## Install params

For packages that need user input at install time. The richest example is
`django_meta`, which uses boolean gates, defaults, `show_if`, and
`message_before_prompt`:

```python
# djdevx/packages/django_meta/__init__.py
from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from ...utils.installable.types import InstallParam
from .._registry import register


@register
class DjangoMetaPackage(BasePackage):
    name: str = "django-meta"
    display_name: str = "Django Meta"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-meta", kind="pypi")]

    install_params: list[InstallParam] = [
        InstallParam(
            name="site_protocol",
            default="https",
            prompt="Please enter your site protocol (http/https)",
        ),
        InstallParam(
            name="use_og_properties",
            type_=bool,
            default=True,
            prompt="Enable OpenGraph properties (Facebook, LinkedIn, WhatsApp)?",
        ),
        # Gated group: only prompted if configure_facebook is True
        InstallParam(
            name="configure_facebook",
            type_=bool,
            default=False,
            prompt="Do you want to configure Facebook/OpenGraph settings?",
        ),
        InstallParam(
            name="fb_app_id",
            show_if="configure_facebook",
            message_before_prompt="\nGet your App ID from: https://developers.facebook.com/apps/",
            prompt="Enter your Facebook App ID (numeric, e.g., 123456789012345) or leave empty",
        ),
    ]
```

Values from `install_params` are passed to Jinja2 templates as context.

## Exclusive variants

Use `exclusive_variants=True` when variants are mutually exclusive backends.
Each variant has its own `template_path`, so templates live in subdirectories.

```python
# djdevx/packages/django_storages/__init__.py
from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from ...utils.installable.types import Variant
from .._registry import register


@register
class StoragesPackage(BasePackage):
    name: str = "django-storages"
    display_name: str = "Django Storages"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-storages[s3,azure,google]", kind="pypi")
    ]
    exclusive_variants: bool = True
    variants: dict[str, Variant] = {
        "s3": Variant(
            name="s3",
            display_name="Amazon S3",
            template_path="s3",
        ),
        "azure": Variant(
            name="azure",
            display_name="Azure Blob Storage",
            template_path="azure",
        ),
        "google": Variant(
            name="google",
            display_name="Google Cloud Storage",
            template_path="google",
        ),
    }
```

```
djdevx/packages/django_storages/templates/
├── s3/
│   └── settings/packages/django_storages_s3.py
├── azure/
│   └── settings/packages/django_storages_azure.py
└── google/
    └── settings/packages/django_storages_google.py
```

Exclusive variants can also declare their own `install_params` per backend —
see `django_anymail`, where the `mailgun` variant collects an `is_europe`
boolean that the other four providers don't need.

## Additive variants

Use `exclusive_variants=False` when users can install multiple variants at
once. `required=True` variants are auto-installed with the parent.
`django_allauth` is the showcase: an account module plus optional mfa and
oidc_provider variants.

```python
# djdevx/packages/django_allauth/__init__.py
from .._base import BasePackage
from djdevx.utils.types.pixi_types import PixiPackageSpec
from ...utils.installable.types import InstallParam, Variant
from .._registry import register
from ...utils.generators import generate_rsa_private_key


@register
class AllauthPackage(BasePackage):
    name: str = "django-allauth"
    display_name: str = "Django Allauth"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-allauth<66")]
    exclusive_variants: bool = False
    variants: dict[str, Variant] = {
        "account": Variant(
            name="account",
            display_name="Account",
            required=True,
            template_path="account",
            install_params=[
                InstallParam(
                    name="email_subject_prefix",
                    prompt="Subject prefix for email messages",
                ),
                InstallParam(
                    name="enable_login_by_code",
                    type_=bool,
                    default=True,
                    prompt="Enable login by code",
                ),
            ],
        ),
        "mfa": Variant(
            name="mfa",
            display_name="MFA (Multi-Factor Authentication)",
            template_path="mfa",
            install_params=[
                InstallParam(name="enable_totp", type_=bool, default=True),
                InstallParam(name="totp_period", type_=int, default=30),
                InstallParam(name="totp_digits", type_=int, default=6),
            ],
        ),
        "oidc_provider": Variant(
            name="oidc_provider",
            display_name="OIDC Provider",
            template_path="oidc_provider",
            secret_generators={
                "idp_oidc_private_key": generate_rsa_private_key,
            },
        ),
    }
```

## Secret generators

For settings templates with `SecretStr` fields that should be auto-generated,
map the field name to a generator. The generator runs when `secrets init dev`
discovers the field and no secret file exists yet.

```python
from djdevx.utils.generators import generate_rsa_private_key

secret_generators: dict[str, Callable] = {
    "idp_oidc_private_key": generate_rsa_private_key,
}
```

Generators can live on the package itself or on individual variants (see the
allauth `oidc_provider` variant above). See
[Secret Generators](creating-an-installable.md#secret-generators) for the full
reference.

## Custom pre/post hooks

Packages commonly override hooks to modify generated files. The convention is
a mutate / revert pair: mutate in `after_copy_templates()`, undo in
`before_pixi_remove()`.

### Modify the user model (django-guardian)

```python
# djdevx/packages/django_guardian/__init__.py
@register
class DjangoGuardianPackage(BasePackage):
    name: str = "django-guardian"
    display_name: str = "Django Guardian"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-guardian")]

    def after_copy_templates(self) -> None:
        self._modify_user_model()

    def before_pixi_remove(self) -> None:
        self._revert_user_model()

    @property
    def _user_model_path(self):
        return self.structure.root / "users" / "models.py"

    def _modify_user_model(self) -> None:
        path = self._user_model_path
        if not path.exists():
            return
        content = path.read_text()
        if "from guardian.mixins import GuardianUserMixin" not in content:
            content = content.replace(
                "from django.contrib.auth.models import AbstractUser",
                "from django.contrib.auth.models import AbstractUser\nfrom guardian.mixins import GuardianUserMixin",
            )
        if "class User(AbstractUser):" in content:
            content = content.replace(
                "class User(AbstractUser):",
                "class User(AbstractUser, GuardianUserMixin):",
            )
        path.write_text(content)

    def _revert_user_model(self) -> None:
        path = self._user_model_path
        if not path.exists():
            return
        content = path.read_text()
        content = content.replace("\nfrom guardian.mixins import GuardianUserMixin", "")
        content = content.replace(
            "class User(AbstractUser, GuardianUserMixin):",
            "class User(AbstractUser):",
        )
        path.write_text(content)
```

Key points:
- Guard with idempotency checks (`if "..." not in content`) so re-runs are safe.
- Revert must be the exact inverse of the mutation (string or regex replace).
- `_base.html` injection is the most common variant of this pattern
  (`django-htmx`, `django-snakeoil`) — see
  [Lifecycle Hooks](creating-an-installable.md#lifecycle-hooks).

### Touch multiple files (django-tailwind-cli)

`after_copy_templates()` can edit several files — `_base.html`, `.gitignore`,
and `Dockerfile` — and `before_pixi_remove()` reverses all three:

```python
# djdevx/packages/django_tailwind_cli/__init__.py
@register
class DjangoTailwindCliPackage(BasePackage):
    name: str = "django-tailwind-cli"
    display_name: str = "Django Tailwind CLI"
    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("django-tailwind-cli", kind="pypi")
    ]

    def after_copy_templates(self) -> None:
        self._add_dark_mode_include()
        self._update_gitignore()
        self._update_dockerfile()

    def before_pixi_remove(self) -> None:
        self._remove_dark_mode_include()
        self._cleanup_gitignore()
        self._cleanup_dockerfile()
```

### Cleanup after pixi remove (django-allauth)

Use `after_pixi_remove()` for cleanup that must happen after the dependency
is gone — for example removing a directory the package created:

```python
def after_pixi_remove(self) -> None:
    import shutil

    shutil.rmtree(self.structure.root / "authentication", ignore_errors=True)
    (self.structure.root / "static" / "css" / "vendor" / "auth.css").unlink(
        missing_ok=True
    )
```

### Reading install context in hooks

Install-time parameter values are available via `self._install_context`:

```python
def after_copy_templates(self) -> None:
    icon_path = self._install_context.get("icon_path", "")
    if icon_path:
        self._generate_icons(icon_path)
```

## Reverting from the new template (restore_on_remove)

When a package **overwrites** a file that ships with the generated project
(e.g. `applications/asgi.py`), uninstalling must restore the original from
`djdevx/new/templates/`. Use `restore_on_remove` mapping `project_rel →
template_rel`:

```python
# djdevx/packages/channels/__init__.py
@register
class ChannelsPackage(BasePackage):
    name: str = "channels"
    display_name: str = "Channels"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("channels")]
    restore_on_remove: dict[str, str] = {"applications/asgi.py": "applications/asgi.py"}
```

On full remove, `restore_original_templates()` re-copies the original
template over the modified file.

## Package templates directory

```
djdevx/packages/<name>/
├── __init__.py
└── templates/
    ├── settings/
    │   └── packages/
    │       └── <name>.py.j2          # → settings/packages/<name>.py
    └── urls/
        └── packages/
            └── <name>.py.j2          # → urls/packages/<name>.py
```

## Testing

```bash
ddx packages add my-package
ddx packages list                 # verify check mark
ddx packages remove my-package
ddx packages list                 # verify cross mark
```

For packages with variants:

```bash
ddx packages add django-storages -p s3
ddx packages remove django-storages -p s3
```

See [Testing](creating-an-installable.md#testing) for the CLI integration
test pattern and golden-file fixtures.

## Related

- [Common Concepts](creating-an-installable.md) — shared pattern, variants, params, hooks, templates
- [Package Architecture](package-architecture.md) — BasePackage details
- [Installable System](installable-system.md) — Shared infrastructure
- [Template System](template-system.md) — Jinja2 rendering conventions
