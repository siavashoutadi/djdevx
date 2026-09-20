"""Pydantic models for profile and answer file validation."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ProfileNew(BaseModel):
    """Override defaults for ``ddx new`` scaffolding.

    Only non-None values override the interactive defaults.  CLI flags
    always take precedence over profile values.
    """

    model_config = ConfigDict(extra="forbid")

    project_description: Optional[str] = None
    python_version: Optional[str] = None
    git_init: Optional[bool] = None


class ProfileInstallable(BaseModel):
    """A single installable entry in a profile.

    For packages/features with exclusive variants (e.g. anymail), set
    ``variant``.  For additive variants (e.g. allauth), set ``variants``.
    If neither is set, required variants are auto-installed and optional
    variants are skipped.
    """

    model_config = ConfigDict(extra="forbid")

    variant: Optional[str] = None
    variants: Optional[list[str]] = None


class Profile(BaseModel):
    """A complete project profile — defines what to install.

    Example::

        [new]
        python_version = "3.14"

        [packages]
        whitenoise = {}
        django-allauth = { variants = ["account", "mfa"] }
        django-anymail = { variant = "mailgun" }

        [features]
        pwa = {}

        [frameworks]
        bootstrap = {}

        [database]
        postgres = {}

        [cache]
        redis = {}
    """

    new: ProfileNew = ProfileNew()
    packages: dict[str, ProfileInstallable] = {}
    features: dict[str, ProfileInstallable] = {}
    frameworks: dict[str, ProfileInstallable] = {}
    database: dict[str, ProfileInstallable] = {}
    cache: dict[str, ProfileInstallable] = {}


class AnswerSet(BaseModel):
    """Answers for a single installable's install parameters."""

    params: dict[str, Any] = {}


class AnswersFile(BaseModel):
    """Pre-filled answers for install parameters, keyed by section and name.

    Example::

        [packages.django-allauth.mfa]
        enable_totp = true
        totp_issuer = "MyApp"

        [packages.django-anymail]
        is_europe = false

        [features.pwa]
        app_name = "My App"
        short_name = "MyApp"
        icon_path = "static/images/logo.png"
    """

    packages: dict[str, Any] = {}
    features: dict[str, Any] = {}
    frameworks: dict[str, Any] = {}
    database: dict[str, Any] = {}
    cache: dict[str, Any] = {}
