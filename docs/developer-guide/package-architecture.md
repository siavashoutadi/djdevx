# Package Architecture

Packages are the most complex installable type. They support variants,
install-time parameters, secret generation, and template overrides.

## BasePackage

`BasePackage` (`djdevx/providers/packages/_base.py`) is a thin subclass of the
single `Provider` base (`djdevx/provider.py`) pinned to the `packages` kind:

```python
class BasePackage(Provider):
    kind = PACKAGE_KIND
```

Payload modules live in `djdevx/providers/packages/<name>/` and keep using
`from .._base import BasePackage` / `from .._registry import register`.

### Additional Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `exclusive_variants` | `bool` | If `True`, user picks exactly one variant |
| `variants` | `dict[str, Variant]` | Named variants (backends, providers, etc.) |
| `install_params` | `list[InstallParam]` | Parameters collected at install time |
| `secret_generators` | `dict[str, Callable]` | Maps `SecretStr` field names to generators |

### Variant

A `Variant` represents a backend or optional feature. It extends
`InstallableConfig`:

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier |
| `display_name` | `str` | Human-readable name |
| `required` | `bool` | Auto-installed when the package is added |
| `pixi_packages` | `list[PixiPackageSpec]` | Variant-specific dependencies (set `pixi_feature="dev"` for dev-only) |
| `peer_pixi_packages` | `dict[InstallableRef, list[PixiPackageSpec]]` | Peer-scoped packages for this variant |
| `template_path` | `str` | Override template directory for this variant |
| `install_params` | `list[InstallParam]` | Variant-specific parameters |
| `secret_generators` | `dict[str, Callable]` | Variant-specific secret generators |
| `files_to_remove` | `list[str]` | Files to delete on uninstall |
| `folders_to_remove` | `list[str]` | Folders to delete on uninstall |
| `restore_on_remove` | `dict[str, str]` | Template overrides |
| `needs` | `list[InstallableRef]` | Variant-specific dependencies |

### InstallParam

Declares a CLI parameter collected during install and passed to templates:

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Parameter name (used in template context) |
| `type_` | `type` | Python type (default: `str`) |
| `default` | `Any` | Default value |
| `help` | `str` | Help text for CLI |
| `prompt` | `Optional[str]` | If set, prompts user interactively |
| `show_if` | `Optional[str]` | Only prompt if this other param is truthy |
| `message_before_prompt` | `str` | Message printed before the prompt |
| `hide_input` | `bool` | Use password input (hidden) |

### Variant Behavior

- `exclusive_variants=True` — user picks exactly one variant (e.g., storage backends)
- `exclusive_variants=False` — variants can be combined (e.g., allauth features)
- `required=True` on a variant — auto-installed when the package is added
- Removing the last additive variant removes the entire package

### Install Lifecycle

```
add_installable(cls, name, provider=None):
  1. _auto_install_needs(needs)              ← recursively install dependencies
  2. (variant selection)                     ← exclusive/additive/simple
  3. Installable.add(variant_name, install_kwargs):
     a. before_pixi_install()                ← hook
     b. PixiOps(root).add_packages(packages, variant)  ← pixi add
     c. after_pixi_install()                 ← hook
     d. before_copy_templates()              ← hook
     e. scaffold.copy_templates(installable, variant)  ← Jinja2 render
     f. after_copy_templates()               ← hook
     g. SecretsOps(root).generate()          ← auto-generate secrets
     h. TrackingOps(section).track_install() ← write tracking
```

### Remove Lifecycle

```
remove_installable(cls, name, provider=None):
  1. Installable.remove(variant_name):
     a. before_pixi_remove()                 ← hook
     b. PixiOps(root).remove_packages()      ← pixi remove
     c. after_pixi_remove()                  ← hook
     d. scaffold.cleanup_files()             ← delete generated files
     e. SecretsOps(root).remove()            ← delete secret files
     f. scaffold.restore_originals()         ← restore templates
     g. TrackingOps(section).remove()        ← update tracking
```

### Secret Generation

```python
from djdevx.utils.generators import generate_random_password

@register
class MyPackage(BasePackage):
    secret_generators: dict[str, Callable] = {
        "api_key": generate_random_password,
    }
```

Available generators in `djdevx/utils/generators/`:

| Generator | Description |
|-----------|-------------|
| `generate_random_password(length=64)` | Cryptographically random alphanumeric string |
| `generate_rsa_private_key()` | 2048-bit RSA private key (PEM format) |

### Concrete Examples

Simple package (no variants):

```python
@register
class WhitenoisePackage(BasePackage):
    name: str = "whitenoise"
    display_name: str = "Whitenoise"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("whitenoise<7")]
```

Package with exclusive variants:

```python
@register
class AnymailPackage(BasePackage):
    name: str = "django-anymail"
    display_name: str = "Django Anymail"
    pixi_packages: list[PixiPackageSpec] = [PixiPackageSpec("django-anymail<16")]
    exclusive_variants: bool = True
    variants: dict[str, Variant] = {
        "ses": Variant(name="ses", display_name="Amazon SES", template_path="ses"),
        "brevo": Variant(name="brevo", display_name="Brevo", template_path="brevo"),
    }
```

Package with non-exclusive variants and parameters:

```python
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
                InstallParam(name="email_subject_prefix", prompt="Subject prefix"),
            ],
        ),
        "mfa": Variant(
            name="mfa",
            display_name="MFA",
            template_path="mfa",
            install_params=[...],
        ),
    }
```

## CLI Commands

```
ddx packages add [NAME] [-p provider] [-v]
ddx packages remove [NAME] [-p provider] [-v]
ddx packages list
```

- `-p / --provider` selects a variant
- Interactive mode uses `checkbox` for multi-select
- Packages support batch install/remove (multiple names at once)

## Package Tracking

```toml
[packages.whitenoise]
installed = true
display_name = "Whitenoise"

[packages."django-allauth"]
installed = true
display_name = "Django Allauth"
variants = ["account", "mfa"]
```

## Related

- [Installable System](installable-system.md) — Shared infrastructure
- [Add a Package](adding-a-package.md) — Step-by-step guide
- [Template System](template-system.md) — Jinja2 rendering
- [Pydantic Settings Architecture](pydantic-settings.md) — Settings resolution
