"""Sentry feature — error monitoring, tracing, and log shipping via sentry-sdk.

Scaffolds a top-level ``sentry`` Django app that calls ``sentry_sdk.init()`` from
``SentryConfig.ready()`` (so every process — web, worker, beat, management
commands — is covered), plus settings, a DEBUG-only ``/sentry-debug/``
endpoint, and optional Celery / Celery Beat peer settings.

The DSN is a *required* secret with no default, so this feature never writes a
secret at install time. Django cannot be imported until the operator runs
``ddx settings secrets init dev`` (or ``init prod``), which the install hook
below spells out.
"""

from djdevx.core.console import NestedStep, print_console
from ....installable.models import SCHEDULER, TASK_QUEUE, InstallableRef
from ....utils.types.pixi_types import PixiPackageSpec
from .._base import BaseFeature
from .._registry import register


@register
class SentryFeature(BaseFeature):
    name: str = "sentry"
    display_name: str = "Sentry"
    description: str = "Sentry error monitoring, tracing, and log shipping"

    pixi_packages: list[PixiPackageSpec] = [
        PixiPackageSpec("sentry-sdk==2.70.0", kind="pypi"),
    ]

    peer_pixi_packages: dict[InstallableRef, list[PixiPackageSpec]] = {
        # Empty package lists: the Celery SDK integration ships inside
        # sentry-sdk, so the peers only contribute settings.
        InstallableRef("celery", TASK_QUEUE): [],
        InstallableRef("celery-beat", SCHEDULER): [],
    }

    def after_copy_templates(self, step: NestedStep | None = None) -> None:
        """Print the required next step — the DSN has no default."""
        (step.warning if step else print_console.warning)(
            "Sentry DSN is required but was not configured"
        )
        for line in (
            "Django will not import until the DSN is set. Grab it from"
            " Sentry → your project → Settings → Client Keys, then run:",
            "  ddx settings secrets init dev      (local development)",
            "  ddx settings secrets init prod     (production deployment)",
            "Then open /sentry-debug/ to verify events arrive.",
        ):
            (step.info if step else print_console.info)(line)
