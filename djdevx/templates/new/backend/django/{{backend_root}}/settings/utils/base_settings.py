import os
from pathlib import Path
from typing import Any

from pydantic_core import PydanticUndefined
from pydantic_settings import (
    BaseSettings,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SecretsSettingsSource,
    SettingsConfigDict,
)

_BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _detect_is_dev() -> bool:
    """
    Derive the dev/prod flag from the DEBUG environment variable.

    - DEBUG not set           → True   (default to dev; safe on a developer laptop)
    - DEBUG=1/true/yes        → True
    - DEBUG=0/false/no        → False  (production; all required fields must be supplied)

    Production deployments must set DEBUG=False explicitly.  Failing to do so
    runs the app with dev defaults, which is the correct safe fallback during
    local development and CI runs that do not configure Django.
    """
    debug_raw = os.environ.get("DEBUG")
    if debug_raw is not None:
        return debug_raw.lower() in ("1", "true", "yes")
    return True


IS_DEV: bool = _detect_is_dev()


class _EnvDefaultsSource(InitSettingsSource):
    """
    Lowest-priority settings source.

    Calls the appropriate classmethod on the settings class and passes the
    returned dict to InitSettingsSource, which treats each key/value pair as
    if it were passed as a keyword argument to the constructor.

    Priority order (driven by DEVCONTAINER env var and IS_DEV flag):
      DEVCONTAINER set → get_devcontainer_defaults()
      IS_DEV=True      → get_dev_defaults()
      IS_DEV=False     → get_prod_defaults()
    """

    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        if os.getenv("DEVCONTAINER"):
            defaults = settings_cls.get_devcontainer_defaults()
        elif IS_DEV:
            defaults = settings_cls.get_dev_defaults()
        else:
            defaults = settings_cls.get_prod_defaults()
        super().__init__(settings_cls, init_kwargs=defaults)


class AppBaseSettings(BaseSettings):
    """
    Base class for all per-module settings in this project.

    Subclass this in each settings file and declare only the fields that
    module cares about.  Fields with no Python default are required — pydantic
    raises ValidationError at startup if they are not supplied by any source.
    Fields that are optional in production should keep a sensible Python default.

    Dev/devcontainer defaults are provided by overriding get_dev_defaults() and
    get_devcontainer_overrides() in each subclass.  os.environ, .env, and secret
    files always win over these class-level defaults.

    Source priority (highest → lowest):
      1. os.environ
      2. backend/.env                    gitignored; personal/CI override
      3. /run/configs/app-config         Swarm Config / K8s ConfigMap (lower prio than .env)
      4. /run/secrets/                   Swarm Secret / K8s Secret volume
      5. backend/.secrets/               local secrets directory (gitignored)
      6. _EnvDefaultsSource              get_dev/devcontainer/prod_defaults()
      7. field-level Python defaults

    List-typed fields (e.g. allowed_hosts) must be set as JSON arrays when
    supplied via environment variables: ALLOWED_HOSTS=["127.0.0.1","example.com"]
    """

    model_config = SettingsConfigDict(
        # Multi-file dotenv: /run/configs/app-config is loaded first (lower priority),
        # backend/.env is loaded second and takes priority (personal/CI override).
        # Missing files are silently skipped by pydantic-settings.
        env_file=(Path("/run/configs/app-config"), _BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Each subclass reads only its own declared fields.  Unrecognised
        # variables from any source are silently skipped so all modules can
        # coexist in the same process without collision.
        extra="ignore",
    )

    @classmethod
    def get_dev_defaults(cls) -> dict[str, Any]:
        """Hardcoded defaults for local runserver. Override in each subclass."""
        return {}

    @classmethod
    def get_devcontainer_overrides(cls) -> dict[str, Any]:
        """
        Values that differ inside a devcontainer (e.g. Docker service hostnames).
        Override in each subclass.  Applied on top of get_dev_defaults().
        """
        return {}

    @classmethod
    def get_devcontainer_defaults(cls) -> dict[str, Any]:
        """Dev defaults merged with devcontainer-specific overrides."""
        return {**cls.get_dev_defaults(), **cls.get_devcontainer_overrides()}

    @classmethod
    def get_prod_defaults(cls) -> dict[str, Any]:
        """Defaults for production contexts. Returns empty — prod must be explicit."""
        return {}

    @classmethod
    def required_secrets(cls) -> list[str]:
        """
        Returns the names of all fields that have no Python default.

        These fields raise ValidationError at startup if not supplied by any
        source.  Useful for management commands that audit deployment readiness.
        """
        return [
            name
            for name, field in cls.model_fields.items()
            if field.default is PydanticUndefined and field.default_factory is None
        ]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources: list[PydanticBaseSettingsSource] = [
            env_settings,  # os.environ
            dotenv_settings,  # /run/configs/app-config, then backend/.env
        ]

        # Secrets dirs are added conditionally to avoid warnings about
        # missing paths.  Container secrets (/run/secrets/) take priority
        # over local secrets (backend/.secrets/).
        prod_secrets = Path("/run/secrets")
        if prod_secrets.exists():
            sources.append(
                SecretsSettingsSource(settings_cls, secrets_dir=prod_secrets)
            )

        local_secrets = _BASE_DIR / ".secrets"
        if local_secrets.exists():
            sources.append(
                SecretsSettingsSource(settings_cls, secrets_dir=local_secrets)
            )

        sources.append(_EnvDefaultsSource(settings_cls))
        return tuple(sources)
