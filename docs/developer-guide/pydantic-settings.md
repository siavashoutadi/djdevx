# Pydantic Settings Architecture

djdevx projects use `pydantic-settings` for all configuration management.
Settings are organized into typed `AppBaseSettings` subclasses that define
every configurable value — secrets, env vars, and application settings —
through a single source of truth. The `SettingCollector` discovers these
classes at runtime by AST-parsing the generated project's settings files,
enabling CLI commands that list configs, show defaults, and manage secrets
across dev and production environments.

## Core Concepts

### pydantic-settings

[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
is the official settings management library for pydantic. It extends
`BaseModel` with the ability to read field values from environment variables,
dotenv files, secret files, and custom sources — all resolved through a
configurable priority chain.

Every settings class in a djdevx project is a `BaseSettings` subclass. This
means each field:

- Has a **type annotation** validated at instantiation time
- Can be populated from environment variables by name
- Falls back through a **priority chain** (env → dotenv → secrets → defaults)
- Supports **per-field defaults** at the Python level

### Why this approach

Before pydantic-settings, Django projects typically scatter configuration
across `settings.py`, `os.environ` lookups, and ad-hoc `.env` parsers. The
result is duplicated logic, untracked defaults, and no single command to
answer "what config does this project need?".

With typed settings classes:

- **Single source of truth** — Every configurable value appears exactly once
  as an annotated field on an `AppBaseSettings` subclass. No parallel
  declarations anywhere.
- **Type safety** — A misconfigured field fails at instantiation, not at
  runtime when the value is first used.
- **Discoverable** — The `SettingCollector` can AST-parse all settings files
  to produce a complete inventory without importing or executing the project.
- **Env var friendly** — pydantic-settings maps field names to env vars
  automatically (e.g., `debug -> DEBUG`, `postgres_server -> POSTGRES_SERVER`).

### SettingsConfigDict

Every `AppBaseSettings` subclass uses a `model_config` to control how
pydantic-settings resolves values:

```python
model_config = SettingsConfigDict(
    env_file=(Path("/run/configs/app-config"), _BASE_DIR / ".env"),
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",
)
```

- **`env_file`** — A tuple of dotenv files loaded in order. `/run/configs/app-config`
  (Docker Swarm Config / K8s ConfigMap) is listed first but has *lower* priority
  than `.env`. pydantic-settings reads all of them and merges them into a single
  dict, with later files overriding earlier ones.
- **`case_sensitive=False`** — Field `postgres_server` matches `POSTGRES_SERVER`,
  `postgres_server`, `Postgres_Server`, etc.
- **`extra="ignore"`** — Allows multiple settings modules to coexist. Each
  `AppBaseSettings` subclass only extracts the fields it knows about and silently
  ignores unrelated env vars.

## AppBaseSettings

Every settings class in a generated project inherits from `AppBaseSettings`.
This base class, defined in `settings/utils/base_settings.py`, provides:

- Common `model_config` (dotenv files, encoding, case sensitivity)
- Lifecycle hooks for dev, devcontainer, and production defaults
- Custom settings source priority via `settings_customise_sources()`

```python
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


def _detect_is_dev() -> bool:
    debug_raw = os.environ.get("DEBUG")
    if debug_raw is not None:
        return debug_raw.lower() in ("1", "true", "yes")
    return True


IS_DEV: bool = _detect_is_dev()


class _EnvDefaultsSource(InitSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        if os.getenv("DEVCONTAINER"):
            defaults = settings_cls.get_devcontainer_defaults()
        elif IS_DEV:
            defaults = settings_cls.get_dev_defaults()
        else:
            defaults = settings_cls.get_prod_defaults()
        super().__init__(settings_cls, init_kwargs=defaults)


class AppBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(Path("/run/configs/app-config"), Path("backend/.env")),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {}

    @classmethod
    def get_devcontainer_overrides(cls) -> dict[str, Any]:
        return {}

    @classmethod
    def get_devcontainer_defaults(cls) -> dict[str, Any]:
        return {**cls.get_dev_defaults(), **cls.get_devcontainer_overrides()}

    @classmethod
    def get_prod_defaults(cls) -> dict[str, Any]:
        return {}

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            file_secret_settings,
            _EnvDefaultsSource(settings_cls),
        )
```

### Lifecycle methods

| Method | When called | Purpose |
|---|---|---|
| `get_dev_defaults()` | Dev mode (`IS_DEV=True`, no `DEVCONTAINER`) | Safe defaults for local development |
| `get_devcontainer_overrides()` | `DEVCONTAINER` is set | Values that differ inside Docker (e.g., service hostnames) |
| `get_devcontainer_defaults()` | `DEVCONTAINER` is set | Merges `get_dev_defaults()` + `get_devcontainer_overrides()` |
| `get_prod_defaults()` | Production mode (`IS_DEV=False`) | Always returns `{}` — production must be explicit |

### settings_customise_sources

This is the pydantic-settings hook that defines the priority chain. It
receives the default sources from pydantic-settings and returns a custom
tuple. The order determines priority — first source wins:

1. `env_settings` — `os.environ` (highest priority)
2. `dotenv_settings` — Files listed in `model_config.env_file`
3. `file_secret_settings` — Docker secrets (`/run/secrets/`) and
   local secrets (`backend/.secrets/`)
4. `_EnvDefaultsSource` — Dev/prod/devcontainer defaults (lowest)

pydantic-settings iterates through these sources for each field and uses
the first value found. A field is resolved independently — one field might
come from an env var while another from dev defaults.

## Settings Priority Chain

When pydantic-settings resolves a field on an `AppBaseSettings` subclass, it
checks each source in order. The first source that provides a value wins.

```
1. os.environ                         ← Runtime env vars (highest)
2. backend/.env                       ← Gitignored personal/CI override
3. /run/configs/app-config            ← Docker Swarm Config / K8s ConfigMap
4. /run/secrets/<fieldname>           ← Docker Swarm Secret / K8s Secret volume
5. backend/.secrets/<fieldname>       ← Local secrets directory
6. _EnvDefaultsSource                 ← Dev / devcontainer / prod defaults
7. Field-level Python default         ← e.g., port: int = 5432 (lowest)
```

| Level | Source | Mechanism | Dev | Prod |
|---|---|---|---|---|
| 1 | `os.environ` | Runtime env vars | Used if set | Used if set |
| 2 | `backend/.env` | dotenv file | Common override | Not typically used |
| 3 | `/run/configs/app-config` | Config file mounted by orchestrator | Not present | Used in Docker/K8s |
| 4 | `/run/secrets/<name>` | Secret file mounted by orchestrator | Not present | Used in Docker/K8s |
| 5 | `backend/.secrets/<name>` | Per-file secrets (`0o600`) | Main dev source | Not typically used |
| 6 | `_EnvDefaultsSource` | Classmethod defaults | `get_dev_defaults()` | `get_prod_defaults()` |
| 7 | Field default | `field: type = value` | Fallback | Fallback |

The key insight: **levels 1-5 are identical in dev and prod**. The difference
is that dev provides safe defaults at level 6, while prod requires values
from levels 1-5.

## Mode Detection

The generated project uses a two-layer approach:

- **`IS_DEV`** — A module-level boolean that controls which default values
  are applied (dev vs prod defaults).
- **`DEBUG`** — A `bool` field on `DjangoBaseSettings` that controls
  Django-specific debug behavior (toolbar, browsable API, etc.).

Together with the `DEVCONTAINER` env var, this creates a three-tier system:

| Mode | `IS_DEV` | `DEVCONTAINER` | Defaults used |
|---|---|---|---|
| Production | `False` | not set | `get_prod_defaults()` — always `{}` |
| Dev (local laptop) | `True` | not set | `get_dev_defaults()` — safe defaults |
| Dev (VS Code devcontainer) | `True` | `"true"` | `get_devcontainer_defaults()` — dev defaults + service hostnames override |

### Detection function

`_detect_is_dev()` reads the `DEBUG` environment variable. It defaults to
`True` (dev mode) when `DEBUG` is unset — safe for a developer laptop. The
result is stored in the module-level `IS_DEV` constant:

```python
def _detect_is_dev() -> bool:
    debug_raw = os.environ.get("DEBUG")
    if debug_raw is not None:
        return debug_raw.lower() in ("1", "true", "yes")
    return True

IS_DEV: bool = _detect_is_dev()
```

### Default selection in _EnvDefaultsSource

The `_EnvDefaultsSource` (level 6 in the priority chain) consults
`DEVCONTAINER` and `IS_DEV` to decide which classmethod to call:

```python
class _EnvDefaultsSource(InitSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        if os.getenv("DEVCONTAINER"):
            defaults = settings_cls.get_devcontainer_defaults()
        elif IS_DEV:
            defaults = settings_cls.get_dev_defaults()
        else:
            defaults = settings_cls.get_prod_defaults()
        super().__init__(settings_cls, init_kwargs=defaults)
```

`get_devcontainer_defaults()` merges dev defaults with devcontainer overrides:

```python
@classmethod
def get_devcontainer_defaults(cls) -> dict[str, Any]:
    return {**cls.get_dev_defaults(), **cls.get_devcontainer_overrides()}
```

This allows each package to define dev defaults once and only override the
fields that change inside a container (e.g., `postgres_server: "localhost"`
→ `"db"`).

### How DEVCONTAINER is set

The generated `.devcontainer/docker-compose.yaml` sets `DEVCONTAINER=true`
on the devcontainer service:

```yaml
environment:
  DEVCONTAINER: "true"
```

### Consumption patterns

| Pattern | Example | Mechanism |
|---|---|---|
| Gate Django debug features | Show/hide toolbar, browsable API | `from settings.django.base import DEBUG` |
| Skip production config in dev | Don't define S3/email/cloud settings | `from settings.utils.base_settings import IS_DEV` + `if not IS_DEV:` |
| Override hostnames in container | `db` vs `localhost` for postgres | `get_devcontainer_overrides()` |

## Secret vs Non-Secret Fields

pydantic-settings treats all fields uniformly during resolution, but
`SecretStr` fields get special handling in the tooling and at runtime.

### Classification

| Classification | Type | Dev source | Container source | Redacted in logs |
|---|---|---|---|---|
| Non-sensitive | `str`, `bool`, `int`, `list`, etc. | `get_dev_defaults()` or `.env` | `/run/configs/app-config` | No |
| Sensitive | `SecretStr`, `Optional[SecretStr]` | `backend/.secrets/<name>` | `/run/secrets/<name>` | Yes |

### SecretStr behavior

`SecretStr` is a pydantic type that wraps a string value:

- **`repr()` shows `'**********'`** — prevents accidental leakage in logs,
  error messages, and debug output
- **`.get_secret_value()` returns the plain string** — used at the point
  where the value is actually needed (e.g., database connection, API call)
- **Hashable and comparable** — two `SecretStr` instances with the same
  value are equal

```python
class DatabaseSettings(AppBaseSettings):
    postgres_password: SecretStr

_db = DatabaseSettings()
# _db.postgres_password        → SecretStr('**********')
# _db.postgres_password.get_secret_value()  → "actual-password"
# repr(_db.postgres_password)  → 'SecretStr('**********')'
```

### How classification drives CLI behavior

When the `SettingCollector` discovers a field:

- **`SecretStr` fields** → Added to `CollectedSettings.secrets`. CLI commands
  create separate files (one per secret) under `.secrets/` or `.secrets.prod/`.
  Each file is written with `0o600` permissions inside a `0o700` directory.
- **Non-SecretStr fields** → Added to `CollectedSettings.config_vars`. CLI
  commands create a single `.env.prod` file in `KEY=VALUE` format.

### Generator callables

Some secrets have associated generator functions — callables that produce a
random value (password, API key, RSA private key). These are registered via
`secret_generators` on package classes:

```python
class OidcProviderPackage(BasePackage):
    secret_generators = {
        "idp_oidc_private_key": generate_rsa_private_key,
    }
```

The `SettingCollector` picks these up from the package registry and attaches
them to the corresponding `SecretInfo`. When the CLI runs `secrets init dev`,
it auto-generates values for secrets that have a generator and are not yet
present on disk.

## The Settings Module System

The generated Django project's settings are split across multiple files in a
structured directory:

```
backend/
  settings/
    __init__.py            ← Dynamic loader — imports everything
    utils/
      base_settings.py     ← AppBaseSettings, IS_DEV, _EnvDefaultsSource
    django/
      __init__.py
      base.py              ← DjangoBaseSettings (SECRET_KEY, DEBUG, ALLOWED_HOSTS, …)
      auth.py              ← AUTH_USER_MODEL, password validators
      database.py          ← Database config (SQLite by default, replaced by postgres)
      email.py.j2          ← Email backend config (Jinja2 template)
      i18n.py              ← Internationalization
      logging.py           ← Logging levels and formatters
      sessions.py          ← Session engine
      staticfiles.py       ← Static/media URL config
      storages.py          ← Storage backends
    packages/
      __init__.py          ← Empty — populated by package install
      django_debug_toolbar.py
      djangorestframework.py
      …                    ← One file per installed package
    apps/
      __init__.py          ← Empty — for developer-defined settings
```

### Dynamic loader

`settings/__init__.py` discovers and loads every `.py` file in the three
subdirectories via `exec()`:

```python
import os
from pathlib import Path
from glob import glob

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_DIR = Path(__file__).resolve().parent
DJANGO_SETTINGS_DIR = SETTINGS_DIR / "django"
PACKAGES_SETTINGS_DIR = SETTINGS_DIR / "packages"
APPS_SETTINGS_DIR = SETTINGS_DIR / "apps"

for settings_dir in (DJANGO_SETTINGS_DIR, PACKAGES_SETTINGS_DIR, APPS_SETTINGS_DIR):
    for f in sorted(settings_dir.glob("*.py")):
        if f.name == "__init__.py":
            continue
        with open(f) as fh:
            exec(compile(fh.read(), f, "exec"), globals())
```

Files are loaded **in alphabetical order** within each subdirectory (`django/`
first, then `packages/`, then `apps/`). This means:

- `django/base.py` runs first — defines `SECRET_KEY`, `DEBUG`, `INSTALLED_APPS`
- `django/*.py` files run next — add auth, logging, database, etc.
- `packages/*.py` files run last — each appends to `INSTALLED_APPS`, adds
  middleware, and defines its own settings class

### Module-level instantiation pattern

Each settings file that uses `AppBaseSettings` instantiates its class at
module load time and exports the resolved values:

```python
class DjangoBaseSettings(AppBaseSettings):
    secret_key: SecretStr
    debug: bool
    allowed_hosts: list[str]
    csrf_trusted_origins: list[str]

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {
            "debug": True,
            "allowed_hosts": ["127.0.0.1", "localhost", "0.0.0.0"],
            "csrf_trusted_origins": [
                "http://localhost:8000",
                "http://127.0.0.1:8000",
            ],
        }

_base = DjangoBaseSettings()  # ← Triggers resolution via priority chain

SECRET_KEY: str = _base.secret_key.get_secret_value()
DEBUG: bool = _base.debug
ALLOWED_HOSTS: list[str] = _base.allowed_hosts
```

The `_base = ClassName()` line triggers pydantic-settings to resolve every
field through the full priority chain. If a required field has no value in
any source, instantiation raises a `ValidationError`.

### The exec() execution model

Because all files are loaded via `exec()` into the same namespace (`globals()`),
each settings file can import from `settings.django.base` as if it were a
regular Python module:

```python
from settings.django.base import INSTALLED_APPS, MIDDLEWARE
```

This works because `settings.django.base` is a real module on `sys.path`,
and the `exec()` call updates `sys.modules["settings.django.base"]` with the
loaded globals. This is the mechanism that makes the split-settings approach
possible without Django knowing about it — Django just imports `settings`
and finds everything already loaded.

## SettingCollector

`SettingCollector` is the runtime engine that discovers all settings classes
in a generated project without importing or executing the project's code.
It uses Python's `ast` module to parse settings files and extract field
information.

### When it runs

The `SettingCollector` is used exclusively by CLI commands — never at Django
runtime. It powers `ddx backend django settings secrets list/init/verify`
and `ddx backend django settings configs list/init/verify`.

### How AST parsing works

```
1. Scan three directories:
   settings/django/      — Core Django settings
   settings/packages/    — Installed package settings
   settings/apps/        — User application settings

2. For each .py file:
   a. Parse source into AST
   b. Find classes that inherit from AppBaseSettings
   c. For each class:
      - Extract annotated field names and type annotations
      - Classify as SecretStr (SecretStr / Optional[SecretStr]) or config var
      - Extract class-level default values
      - AST-parse get_dev_defaults() and get_prod_defaults() return values
      - Attach dev/prod defaults to each field

3. Build generators index from package registry:
   - BasePackage._generator_packages
   - DATABASE_REGISTRY + CACHE_REGISTRY
   - Hardcoded secret_key generator

4. Return CollectedSettings with deduplicated secrets + config_vars
```

### AST vs import

Parsing via AST (rather than `import`) is a deliberate design choice:

| Aspect | AST parsing | Import |
|---|---|---|
| Safety | No code execution | Executes all module-level code |
| Speed | Fast — pure syntax analysis | Slower — imports dependencies |
| Dependencies | None — pure Python stdlib | Requires project dependencies installed |
| Accuracy | Can't resolve dynamic defaults | Full runtime accuracy |

The project may not even have its dependencies installed when CLI commands
run (e.g., right after `ddx new backend django`). AST parsing works in all
environments.

### SecretStr detection

`_is_secret_str()` handles all common `SecretStr` annotation patterns:

```python
field: SecretStr                   # Simple
field: Optional[SecretStr]         # Optional
field: Union[SecretStr, None]      # Union style
field: SecretStr | None            # PEP 604
```

### Generators index

The `_build_generators_index()` method creates a flat mapping from field
name to generator callable. It sources generators from:

1. **`BasePackage._generator_packages`** — All `BasePackage` subclasses that
   have non-empty `secret_generators` are auto-registered via `__init_subclass__`.
   Each package declares which secrets it can auto-generate:

   ```python
   class OidcProviderPackage(BasePackage):
       secret_generators = {
           "idp_oidc_private_key": generate_rsa_private_key,
       }
   ```

2. **Database and cache registries** — Plugins from `DATABASE_REGISTRY` and
   `CACHE_REGISTRY` are scanned for `secret_generators`.

3. **Hardcoded `secret_key`** — Always registered, uses a 64-character random
   password generator.

The index is built once and cached on the collector instance.

### Output structure

```python
@dataclass
class CollectedSettings:
    secrets: list[SecretInfo]        # One per SecretStr field
    config_vars: list[ConfigVarInfo] # One per non-SecretStr field

@dataclass
class SecretInfo:
    name: str                             # Field name (e.g., "postgres_password")
    source_file: Path                     # File that defines this field
    generator: Callable[[], str] | None   # Auto-generator (if any)
    dev_default: Any                      # Value from get_dev_defaults()
    prod_default: Any                     # Value from get_prod_defaults()

@dataclass
class ConfigVarInfo:
    name: str                             # Field name (e.g., "postgres_server")
    source_file: Path                     # File that defines this field
    type_annotation: str                  # e.g., "str", "bool", "list[str]"
    dev_default: Any                      # Value from get_dev_defaults()
    prod_default: Any                     # Value from get_prod_defaults()
```

Fields are **deduplicated by name** — the first occurrence wins. This means a
package settings file can define `postgres_password` and it won't be
overwritten if `django/database.py` also defines it (it doesn't, but the
mechanism protects against accidental conflicts).

### What AST Parsing Extracts

| Item | Source in File |
|---|---|
| Secret field names | `field: SecretStr` annotation |
| Config var names | Non-SecretStr annotated fields |
| Type annotations | The annotation AST node (unparsed back to string) |
| Dev defaults | `get_dev_defaults()` return dict literal |
| Prod defaults | `get_prod_defaults()` return dict literal |
| Class-level defaults | `field: type = value` or `Field(default=value)` |
| File ownership | The file path itself |

## CLI Tooling

The CLI commands under `ddx backend django settings` give developers full
visibility and control over their project's settings. All commands use the
`SettingCollector` to discover fields, then apply environment-specific
resolution chains to determine source and value.

### Commands overview

```
ddx backend django settings
  secrets
    list [dev|prod]       → Display all SecretStr fields with source and status
    init [dev|prod]       → Generate missing secrets (auto-generate or prompt)
    verify [dev|prod]     → Exit with code 1 if any secret is missing
  configs
    list [dev|prod]       → Display all non-SecretStr fields with source and value
    init prod             → Prompt for missing production config vars
    verify [dev|prod]     → Exit with code 1 if any config var is missing
```

### Resolution chains

The resolution chain for listing and verifying differs between dev and prod:

#### Secrets resolution

| Step | Dev | Prod |
|---|---|---|
| 1 | `backend/.secrets/<name>` | `/run/secrets/<name>` |
| 2 | `/run/secrets/<name>` | `backend/.secrets.prod/<name>` |
| 3 | `get_dev_defaults()` | `get_prod_defaults()` |
| 4 | **MISSING** | **MISSING** |

#### Config vars resolution

| Step | Dev | Prod |
|---|---|---|
| 1 | `os.environ` | `os.environ` |
| 2 | `backend/.env` | `/run/configs/app-config` |
| 3 | `get_dev_defaults()` | `backend/.env.prod` |
| 4 | **MISSING** | `get_prod_defaults()` |
| 5 | — | **MISSING** |

### secrets init dev

The most commonly used command. For each `SecretStr` field discovered by the
`SettingCollector`:

1. **If already present** in `backend/.secrets/` or `/run/secrets/` → skip
2. **If `get_dev_defaults()` provides a value** → skip (dev defaults are safe)
3. **If `secret.generator` is not None** → auto-generate and write to `backend/.secrets/<name>`
4. **Otherwise** → prompt the user for a value and write to `backend/.secrets/<name>`

Secrets are written as individual files using `SecretManager`:

```python
# backend/.secrets/postgres_password  (0o600, inside 0o700 directory)
```

### secrets init prod

Same flow as dev, but:

- Writes to `backend/.secrets.prod/<name>` (separate directory for production)
- Does NOT skip fields with dev defaults — production requires explicit values
- Prompts for ALL secrets unless already present

### configs init prod

For each non-SecretStr field discovered by the `SettingCollector`:

1. **If already present** in `os.environ`, `backend/.env`, or `backend/.env.prod` → skip
2. **Prompt the user** with the field's type annotation for validation
3. **Write to `backend/.env.prod`** in `KEY=VALUE` format via `dotenv.set_key()`

`setup_readline()` is called before any prompts, giving readline history
(up/down arrow navigation) and full line editing. History is persisted to
`~/.djdevx/readline_history` across sessions.

Input is validated against the pydantic type using `pydantic.TypeAdapter`:

```python
adapter = TypeAdapter(annotation_str)  # e.g., TypeAdapter(list[str])
parsed = adapter.validate_python(raw_input)
```

### list and verify

- **`list`** displays a Rich table with columns: status (check/cross), field name,
  type, source (which step in the chain resolved it), and resolved value.
- **`verify`** exits with code 0 if all fields have a value, code 1 if any
  are missing. Used in CI/CD pipelines and devcontainer lifecycle hooks.

## Adding Settings to a Package

Every package that needs configuration follows the same pattern: create a
settings template file that defines an `AppBaseSettings` subclass, place it
in the correct directory, and (optionally) register secret generators on the
package class.

### Template file location

The template directory mirrors the target location in the generated project.
There are two conventions:

#### Convention A: Standard packages (most common)

```
djdevx/templates/django/<package_name>/
  settings/packages/<filename>.py
  urls/packages/<filename>.py      (optional)
  templates/...                     (optional Django app templates)
  static/...                        (optional static files)
```

The file is copied to `backend/settings/packages/<filename>.py` in the
generated project.

#### Convention B: Core Django settings (database, cache)

```
djdevx/templates/django/<package_type>/<variant>/
  {{backend_root}}/settings/django/<filename>.py
```

The `{{backend_root}}` Jinja2 variable (typically `backend`) is rendered
during template copy. The file ends up at `backend/settings/django/<filename>.py`.

#### Convention C: Sub-packages (grouped under a directory)

For multi-provider packages (allauth, anymail, storages):

```
djdevx/templates/django/django_allauth/
  account/
    settings/packages/django_allauth_account.py.j2
    urls/packages/django_allauth_account.py.j2
  oidc_provider/
    settings/packages/django_allauth_oidc_provider.py
```

The settings filename is auto-derived from the Python package file location:
- `packages/django_allauth/account.py` → template dir `django_allauth/account/`
  → settings file `django_allauth_account.py`
- `packages/django_allauth/oidc_provider.py` → template dir `django_allauth/oidc_provider/`
  → settings file `django_allauth_oidc_provider.py`

### Template flavors

There are four patterns for settings templates, depending on the package's
complexity:

#### Flavor 1: AppBaseSettings subclass (configurable fields)

Use when the package has configurable values, especially secrets:

```python
from typing import Any
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings


class MyPackageSettings(AppBaseSettings):
    api_key: SecretStr
    endpoint: str

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        return {"endpoint": "http://localhost:8000"}

    @classmethod
    def get_devcontainer_overrides(cls) -> dict[str, Any]:
        return {"endpoint": "http://web:8000"}


_mypackage = MyPackageSettings()
MYPACKAGE_API_KEY = _mypackage.api_key.get_secret_value()
MYPACKAGE_ENDPOINT = _mypackage.endpoint
```

This pattern creates discoverable secrets and config vars that the CLI can
list, verify, and initialize.

#### Flavor 2: Direct Django config injection (no AppBaseSettings)

Use when the package just modifies `INSTALLED_APPS` / `MIDDLEWARE` and has
no configurable fields:

```python
from settings.django.base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS += ["my_package"]
MIDDLEWARE += ["my_package.middleware.MyMiddleware"]
```

#### Flavor 3: Conditional AppBaseSettings (IS_DEV gating)

Use when the package needs different behavior in dev vs prod:

```python
from settings.django.base import INSTALLED_APPS
from settings.utils.base_settings import AppBaseSettings, IS_DEV

INSTALLED_APPS += ["corsheaders"]

if IS_DEV:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    class CorsSettings(AppBaseSettings):
        cors_allowed_origins: list[str]
        cors_allowed_origin_regexes: list[str] = []

    _cors = CorsSettings()
    CORS_ALLOWED_ORIGINS = _cors.cors_allowed_origins
    CORS_ALLOWED_ORIGIN_REGEXES = _cors.cors_allowed_origin_regexes
```

In dev mode, CORS allows all origins (no configuration needed). In
production, the settings class is instantiated and requires explicit
`cors_allowed_origins` from env vars or config files.

#### Flavor 4: Jinja2-rendered (.j2 extension)

Use when the file content depends on `install_params` captured during
package installation:

```jinja2
from settings.django.base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS += ["authentication", "allauth", "allauth.account"]
MIDDLEWARE += ["allauth.account.middleware.AccountMiddleware"]

LOGIN_URL = "/{{ account_url_prefix }}/login"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "{{ email_subject_prefix }}"
{% if enable_login_by_code %}
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
{% endif %}
```

The `.j2` extension triggers Jinja2 content rendering. The suffix is
stripped in the output file so it becomes a plain `.py` file.

### Registering secret generators

If the settings template has `SecretStr` fields that should be auto-generated
(not prompted), add a `secret_generators` dict on the package class:

```python
from djdevx.utils.generators import generate_random_password

class MyPackage(BasePackage):
    name = "my-package"
    packages = ["my-package"]

    secret_generators = {
        "api_key": lambda: generate_random_password(length=32),
    }
```

The key must match the field name in the settings template exactly. When
`secrets init dev` runs and the secret doesn't exist yet, it calls the
generator and writes the result to `backend/.secrets/api_key`.

### Install params as template context

When a template uses Jinja2 rendering (`.j2` extension), the `install_params`
become template context variables:

```python
class MyPackage(BasePackage):
    install_params = [
        InstallParam(name="api_url_prefix", default="api", help="URL prefix for API endpoints"),
        InstallParam(name="enable_feature_x", type_=bool, default=True, help="Enable feature X"),
    ]
```

During `ddx backend django packages my-package install`, the CLI prompts for
each parameter and passes the values as Jinja2 context when rendering templates.

### Full example: Adding a new package with settings

**Step 1: Create the package file**

`djdevx/backend/django/packages/my_package.py`:

```python
from ._base import BasePackage
from djdevx.utils.generators import generate_random_password


class MyPackage(BasePackage):
    name = "my-package"
    packages = ["my-package"]
    secret_generators = {
        "my_package_api_key": lambda: generate_random_password(length=32),
    }


_pkg = MyPackage(__file__)
app = _pkg.app
```

**Step 2: Create the settings template**

`djdevx/templates/django/my_package/settings/packages/my_package.py`:

```python
from typing import Any
from pydantic import SecretStr
from settings.utils.base_settings import AppBaseSettings
from settings.django.base import INSTALLED_APPS


class MyPackageSettings(AppBaseSettings):
    my_package_api_key: SecretStr
    my_package_endpoint: str = "http://localhost:8000"


_mypackage = MyPackageSettings()
MYPACKAGE_API_KEY = _mypackage.my_package_api_key.get_secret_value()
MYPACKAGE_ENDPOINT = _mypackage.my_package_endpoint

INSTALLED_APPS += ["my_package"]
```

**Step 3: Register in the package registry**

`djdevx/backend/django/packages/__init__.py`:

```python
from .my_package import app as my_package
app.add_typer(my_package, name="my-package")
```

**Step 4: Result**

When `secrets init dev` runs, the `SettingCollector` discovers
`my_package_api_key: SecretStr` and auto-generates it. `secrets list dev`
displays:

```
✓  my_package_api_key   backend/.secrets/my_package_api_key
✓  my_package_endpoint  Dev default
```

When `configs init prod` runs, it prompts for `my_package_endpoint` if not
set and writes it to `.env.prod`.

### Architecture

```
Package definition                    Generated project
─────────────────                     ─────────────────
                                        settings/
MyPackage                                  utils/
  secret_generators = {                      base_settings.py ← AppBaseSettings
    "my_package_api_key": ...              django/
  }                                           base.py
  install_params = [...]                    packages/
                                             my_package.py ← AppBaseSettings subclass
                                               my_package_api_key: SecretStr
Templates                                     my_package_endpoint: str
  my_package/
    settings/packages/          ──copy──▶    apps/
      my_package.py                               (user-defined)
                                                  │
                                                  ▼
                                        SettingCollector (AST parser)
                                                  │
                                                  ▼
                                        ┌───────────────┬─────────────────┐
                                        │ Secrets        │ Config vars      │
                                        │ (SecretStr)    │ (non-SecretStr)  │
                                        └───────┬───────┴────────┬────────┘
                                                │                │
                                                ▼                ▼
                                         ddx settings      ddx settings
                                         secrets init      configs init prod
                                         → .secrets/       → .env.prod
```

`configs init prod` calls `setup_readline()` from `_source.py`, enabling
readline history (up/down arrow navigation), line editing, and proper escape
sequence handling. History is persisted to `~/.djdevx/readline_history`.

No parallel declarations in djdevx source. No manifest files in `.djdevx/`.
Updating a settings file is immediately reflected in all commands.

## Design Rules

1. **Dev defaults are safe** — A developer should be able to run the project
   without any `.env` or `.secrets` file in dev mode. Every settings class
   provides `get_dev_defaults()` that returns values suitable for local
   development (localhost hostnames, debug mode on, permissive CORS, etc.).

2. **Production is explicit** — `get_prod_defaults()` always returns `{}`.
   Every field must be explicitly configured in production via env vars,
   config files, or secrets. This ensures a production deployment can never
   accidentally use an unsafe dev default.

3. **Secrets never logged** — `SecretStr` fields are redacted in logs and
   error messages by pydantic's built-in `SecretStr` implementation. The
   plain value is only accessible via `.get_secret_value()` at the exact
   point it is needed.

4. **Devcontainer auto-detected** — The `DEVCONTAINER` env var, set by
   VS Code's devcontainer runtime, causes `_EnvDefaultsSource` to call
   `get_devcontainer_defaults()` instead of `get_dev_defaults()`. This
   swaps service hostnames (e.g., `localhost` → `db`) without any manual
   configuration.

5. **No hardcoded production values** — All production values come from
   environment variables, mounted config files, or secret stores. The
   only exception is `get_prod_defaults()`, which is always empty and
   serves as a deliberate reminder that production requires explicit
   configuration.
