# Packages — Environment Variables & Secrets Analysis

Analysis of all 39 Django template packages under `djdevx/templates/django/` plus the 3 core settings files under `templates/new/backend/django/`.

---

## Architecture Summary

All settings classes inherit from `AppBaseSettings` (pydantic `BaseSettings`), making **every declared field** an environment variable. Source priority (highest → lowest):

1. `os.environ`
2. `backend/.env`
3. `/run/configs/app-config`
4. `/run/secrets/` — Docker/K8s secrets
5. `backend/.secrets/` — local secrets directory
6. `_EnvDefaultsSource` — calls `get_dev_defaults()`, `get_prod_defaults()`, or `get_devcontainer_defaults()`
7. Field-level Python defaults

The `DEBUG` env var controls `IS_DEV`:
- `DEBUG` not set, `DEBUG=1/true/yes` → `IS_DEV=True` → safe dev defaults applied
- `DEBUG=0/false/no` → `IS_DEV=False` → production mode, all required fields must be supplied

---

## Packages with AppBaseSettings Subclasses

### Legend
- **Class Default**: Python-level default in the field declaration (`field: type = value`)
- **Dev Default**: Value returned by `get_dev_defaults()` (applied when `IS_DEV=True`)
- **Prod Default**: Value returned by `get_prod_defaults()` (applied when `IS_DEV=False`)
- **Auto-Gen?**: Registered in `secret_generators` dict on the `BasePackage` subclass
- **Dev Requirement**: Whether the field has a usable value in dev mode without manual input
- ⓘ = gated by `if not IS_DEV:` — skipped entirely in dev mode

### Core Settings (`templates/new/backend/django/`)

| Package | Field | Type | Class Default | Dev Default | Prod Default | Auto-Gen? | Dev Requirement |
|---|---|---|---|---|---|---|---|
| **base** | `secret_key` | `SecretStr` | — | — | — | ✅ `generate_random_password(64)` | generated at project creation; no runtime fallback |
| | `debug` | `bool` | — | `True` | — | ❌ | ✅ |
| | `allowed_hosts` | `list[str]` | — | `["127.0.0.1", "localhost", "0.0.0.0"]` | — | ❌ | ✅ |
| | `csrf_trusted_origins` | `list[str]` | — | `["http://localhost:8000", "https://localhost:8000", "http://127.0.0.1:8000", "https://127.0.0.1:8000"]` | — | ❌ | ✅ |
| **logging** | `use_rich_logging` | `bool` | `False` | `True` | — | ❌ | ✅ |
| | `console_log_level` | `str` | `"INFO"` | `"DEBUG"` | — | ❌ | ✅ |
| | `django_log_level` | `str` | `"WARNING"` | `"INFO"` | — | ❌ | ✅ |
| | `root_log_level` | `str` | `"WARNING"` | `"INFO"` | — | ❌ | ✅ |
| **email** | `email_backend` | `str` | `"django.core.mail.backends.smtp.EmailBackend"` | `"django.core.mail.backends.console.EmailBackend"` | — | ❌ | ✅ |
| | `django_default_from_email` | `EmailStr` | — | `"noreply@example.com"` | — | ❌ | ✅ |
| | `django_server_email` | `EmailStr` | — | `"server@example.com"` | — | ❌ | ✅ |

### Infrastructure Packages

| Package | Field | Type | Class Default | Dev Default | Prod Default | Auto-Gen? | Dev Requirement |
|---|---|---|---|---|---|---|---|
| **database** | `postgres_server` | `str` | — | `"localhost"` (devcontainer: `"db"`) | — | ❌ | ✅ |
| | `postgres_port` | `int` | `5432` | `5432` | — | ❌ | ✅ |
| | `postgres_db` | `str` | — | `"postgres"` | — | ❌ | ✅ |
| | `postgres_user` | `str` | — | `"postgres"` | — | ❌ | ✅ |
| | `postgres_password` | `SecretStr` | — | `"devpassword"` | — | ❌ | ✅ |
| **cache** | `redis_host` | `str` | — | `"localhost"` (devcontainer: `"cache"`) | — | ❌ | ✅ |
| | `redis_port` | `int` | `6379` | `6379` | — | ❌ | ✅ |
| | `redis_db` | `int` | `1` | `1` | — | ❌ | ✅ |
| | `redis_password` | `SecretStr` | — | `"redis_password"` | — | ❌ | ✅ |
| **channels** | `redis_host` | `str` | — | `"localhost"` (devcontainer: `"cache"`) | — | ❌ | ✅ |
| | `redis_port` | `int` | `6379` | `6379` | — | ❌ | ✅ |
| | `redis_db` | `int` | `1` | `1` | — | ❌ | ✅ |
| | `redis_password` | `SecretStr` | — | `"redis_password"` | — | ❌ | ✅ |

### App / Security Packages

| Package | Field | Type | Class Default | Dev Default | Prod Default | Auto-Gen? | Dev Requirement |
|---|---|---|---|---|---|---|---|
| **django_allow_cidr** | `allowed_cidr_nets` | `list[str]` | `[]` | — | — | ❌ | ✅ |
| **django_cors_headers** ⓘ | `cors_allowed_origins` | `list[str]` | `[]` | N/A (dev: `CORS_ALLOW_ALL_ORIGINS=True`) | — | ❌ | N/A in dev |
| | `cors_allowed_origin_regexes` | `list[str]` | `[]` | N/A | — | ❌ | N/A in dev |
| **django_defender** | `defender_redis_name` | `str` | `"default"` | — | — | ❌ | ✅ |
| | `defender_lockout_url` | `AnyUrl` | — | `"http://localhost:8000/"` | — | ❌ | ✅ |
| **django_health_check** | `health_check_url` | `str` | `"hc"` | — | — | ❌ | ✅ |
| **django_allauth/oidc** | `idp_oidc_private_key` | `SecretStr` | — | — | — | ✅ `generate_rsa_private_key()` | generated at install; no runtime fallback |

### Email Providers (django_anymail) ⓘ — all gated by `if not IS_DEV:`

| Variant | Field | Type | Class Default | Dev Default | Prod Default | Auto-Gen? | Dev Requirement |
|---|---|---|---|---|---|---|---|
| **mailjet** | `anymail_mailjet_api_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| | `anymail_mailjet_secret_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| **ses** | `anymail_ses_access_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| | `anymail_ses_secret_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| | `anymail_ses_region_name` | `str` | — | N/A | — | ❌ | N/A in dev |
| **resend** | `anymail_resend_api_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| **brevo** | `anymail_brevo_api_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| **mailgun** | `anymail_mailgun_api_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| | `anymail_mailgun_sender_domain` | `str` | — | N/A | — | ❌ | N/A in dev |

### File Storage (django_storages) ⓘ — all gated by `if not IS_DEV:`

| Variant | Field | Type | Class Default | Dev Default | Prod Default | Auto-Gen? | Dev Requirement |
|---|---|---|---|---|---|---|---|
| **s3** | `storages_s3_access_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| | `storages_s3_secret_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| | `storages_s3_region_name` | `str` | — | N/A | — | ❌ | N/A in dev |
| | `storages_s3_bucket_name` | `str` | — | N/A | — | ❌ | N/A in dev |
| **google** | `storages_google_credentials` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| | `storages_google_bucket_name` | `str` | — | N/A | — | ❌ | N/A in dev |
| **azure** | `storages_azure_account_key` | `SecretStr` | — | N/A | — | ❌ | N/A in dev |
| | `storages_azure_account_name` | `str` | — | N/A | — | ❌ | N/A in dev |
| | `storages_azure_container_name` | `str` | — | N/A | — | ❌ | N/A in dev |

---

## Packages WITHOUT AppBaseSettings (no env vars)

These 29 packages add apps, middleware, URLs, template tags, or hardcoded Django settings — they read no env vars and declare no secrets.

| Package | Files | What It Configures |
|---|---|---|
| **django_auditlog** | `settings/packages/django_auditlog.py` | Adds `auditlog` app + middleware |
| **django_browser_reload** | `settings/packages/django_browser_reload.py` | Adds `django_browser_reload` app + middleware (gated by `DEBUG`) |
| **django_csp** | `settings/packages/django_csp.py` | Hardcodes `CSP_DEFAULT_SRC`, `CSP_STYLE_SRC`, etc. |
| **django_debug_toolbar** | `settings/packages/django_debug_toolbar.py`, `urls/...` | Adds `debug_toolbar` app + middleware (gated by `DEBUG`) |
| **django_extensions** | `settings/packages/django_extensions.py` | Adds `django_extensions` to INSTALLED_APPS |
| **django_filter** | `settings/packages/django_filter.py` | Adds `django_filters` to INSTALLED_APPS |
| **django_guardian** | `settings/packages/django_guardian.py` | Adds `guardian` app + auth backend |
| **django_htmx** | `settings/packages/django_htmx.py` | Adds `django_htmx` app + middleware |
| **django_import_export** | `settings/packages/django_import_export.py` | Adds `import_export` to INSTALLED_APPS |
| **django_meta** | `settings/packages/django_meta.py.j2` | Jinja2 template; renders `<meta>` tags from template vars |
| **django_oauth_toolkit** | `settings/packages/django_oauth_toolkit.py`, `urls/...` | Hardcodes `OAUTH2_PROVIDER` config; allows `http` in dev |
| **django_permissions_policy** | `settings/packages/django_permissions_policy.py` | Hardcodes permissions policy headers |
| **django_role_permissions** | `settings/packages/django_role_permissions.py` | Adds `rolepermissions` app + `ROLEPERMISSIONS_REGISTER_ADMIN` |
| **django_silk** | `settings/packages/django_silk.py`, `urls/...` | Adds `silk` app + middleware (gated by test detection) |
| **django_simple_history** | `settings/packages/django_simple_history.py` | Adds `simple_history` app + middleware |
| **django_simple_nav** | `settings/packages/django_simple_nav.py` | Adds `simple_nav` to INSTALLED_APPS |
| **django_snakeoil** | `settings/packages/django_snakeoil.py.j2` | Jinja2 template; SEO/social tags from template vars |
| **django_sp_admin** | `settings/packages/django_sp_admin.py` | Inserts `django_sp_admin` before `django.contrib.admin` |
| **django_taggit** | `settings/packages/django_taggit.py` | Adds `taggit` app + `TAGGIT_CASE_INSENSITIVE` |
| **django_tailwind_cli** | `settings/packages/django_tailwind_cli.py` | Adds `django_tailwind_cli` app + hardcoded CSS paths |
| **djangochannelsrestframework** | `settings/packages/djangochannelsrestframework.py` | Adds `channels_rest_api` to INSTALLED_APPS |
| **djangorestframework** | `settings/packages/djangorestframework.py`, `urls/...` | Hardcodes `REST_FRAMEWORK` config (pagination, throttling, auth) |
| **drf_spectacular** | `settings/packages/drf_spectacular.py`, `urls/...` | Adds `drf_spectacular` apps + `SPECTACULAR_SETTINGS` |
| **heroicons** | `settings/packages/heroicons.py` | Adds `heroicons` app + template tag library |
| **pwa** | `pwa/` (views, urls, apps) | Custom app with `manifest.json` / `sw.js` views |
| **startapp** | `startapp/` (j2 templates) | Jinja2 templates for scaffolding new Django apps |
| **tailwind_theme** | (empty directory) | No files |
| **tailwind_ui** | `tailwind_ui/` (tags, views, urls) | Custom app with UI template tags and views |
| **whitenoise** | `settings/packages/whitenoise.py` | Adds middleware + `STORAGES["staticfiles"]` backend |

---

## Registered Auto-Generators

Found in `backend/django/packages/`:

| Package File | Class | Generator | Field |
|---|---|---|---|
| `_base.py` | `BasePackage` (base) | — | (empty base class) |
| `django_allauth/oidc_provider.py` | `OidcProviderPackage` | `generate_rsa_private_key()` | `idp_oidc_private_key` |
| `_registries.py` | `PostgresPlugin` | — | (empty — uses dev defaults) |
| `_registries.py` | `RedisPlugin` | — | (empty — uses dev defaults) |

Additionally, `SettingCollector._build_generators_index()` always registers:
- `secret_key` → `generate_random_password(length=64)`

---

## Devcontainer Overrides

Applied on top of `get_dev_defaults()` when `DEVCONTAINER` env var is set:

| Package | Override |
|---|---|
| **database** | `postgres_server: "db"` (Docker service name) |
| **cache** | `redis_host: "cache"` (Docker service name) |
| **channels** | `redis_host: "cache"` (Docker service name) |

---

## Summary Statistics

| Metric | Count |
|---|---|
| Total `AppBaseSettings` subclasses | **19** |
| Total config fields across all classes | **39** |
| Fields with Python-level class default | **11** (28%) |
| Fields covered by `get_dev_defaults()` | **27** (69%) |
| Fields gated by `IS_DEV` (not needed in dev) | **11** (28%) |
| Fields with registered auto-generator | **2** (`secret_key`, `idp_oidc_private_key`) |
| Fields with generator but **no** runtime `get_dev_defaults()` | **2** (intentional — generated via CLI) |
| Fields with NO fallback in dev AND no generator | **0** |
| Packages with zero env vars | **29** out of 39 |

---

## Gap Analysis

**No real gaps.** Every `SecretStr` field is covered by one of:

1. **`get_dev_defaults()`** — hardcoded safe dev values (e.g., `"devpassword"` for Postgres, `"redis_password"` for Redis)
2. **`IS_DEV` gating** — production-only configs (anymail, storages) are entirely skipped in dev mode
3. **Auto-generator** — keys are generated at package install or via `ddx backend django settings secrets init dev` (`secret_key`, `idp_oidc_private_key`)

The two fields with generators but no `get_dev_defaults()` (`secret_key`, `idp_oidc_private_key`) intentionally force the developer to use the CLI tooling rather than silently falling back to a placeholder at runtime.
