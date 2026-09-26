"""Tests for the Sentry feature."""

import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.core.process import PixiRunner
from djdevx.main import app
from djdevx.utils.project.setting_collector import SettingCollector
from djdevx.utils.templates.manager import TemplateManager
from djdevx.utils.tracking import ProjectTracking, Section
from tests.test_helpers import create_test_django_project

runner = CliRunner()


def _install_feature(name: str) -> None:
    result = runner.invoke(app, ["features", "add", name])
    assert result.exit_code == 0, f"Feature install failed: {result.output}"


def _remove_feature(name: str) -> None:
    result = runner.invoke(app, ["features", "remove", name])
    assert result.exit_code == 0, f"Feature remove failed: {result.output}"


def _install_task_queue(name: str) -> None:
    result = runner.invoke(app, ["task-queue", "add", name])
    assert result.exit_code == 0, f"Task queue install failed: {result.output}"


def _install_scheduler(name: str) -> None:
    result = runner.invoke(app, ["scheduler", "add", name])
    assert result.exit_code == 0, f"Scheduler install failed: {result.output}"


def _template_path(rel: str) -> Path:
    import djdevx

    return Path(djdevx.__file__).resolve().parent / rel


def _assert_sentry_app_exists(root: Path) -> None:
    for name in ("__init__.py", "apps.py", "setup.py", "urls.py", "views.py"):
        assert (root / "sentry" / name).exists(), f"sentry/{name} missing"

    init_content = (root / "sentry" / "__init__.py").read_text()
    assert "setup_sentry" not in init_content, (
        "sentry/__init__.py must not import or run setup (import side effects)"
    )

    apps_content = (root / "sentry" / "apps.py").read_text()
    assert "def ready(self)" in apps_content, (
        "sentry/apps.py must initialize the SDK from AppConfig.ready() so every "
        "process (web, worker, beat, management commands) is covered"
    )
    assert "setup_sentry()" in apps_content, (
        "sentry/apps.py ready() must call setup_sentry()"
    )

    setup_content = (root / "sentry" / "setup.py").read_text()
    assert "sentry_sdk.init(" in setup_content, "sentry/setup.py must init the SDK"
    assert "DjangoIntegration(" in setup_content, (
        "sentry/setup.py must configure the Django integration"
    )
    assert "LoggingIntegration(" in setup_content, (
        "sentry/setup.py must configure the logging integration"
    )
    assert "enable_logs" not in setup_content, (
        "sentry/setup.py must not use the removed enable_logs option"
    )
    assert "capture_sentry_logs" in setup_content, (
        "sentry/setup.py must opt into log capture through capture_sentry_logs"
    )
    assert "_INITIALIZED" in setup_content, (
        "sentry/setup.py must guard against initializing twice in one process"
    )

    views_content = (root / "sentry" / "views.py").read_text()
    assert "1 / 0" in views_content, "sentry/views.py must raise on purpose"

    urls_content = (root / "sentry" / "urls.py").read_text()
    assert 'path("sentry-debug/"' in urls_content, (
        "sentry/urls.py must expose the /sentry-debug/ verification endpoint"
    )


def _assert_sentry_settings_exists(root: Path) -> None:
    settings_file = root / "settings" / "apps" / "sentry.py"
    assert settings_file.exists(), "settings/apps/sentry.py missing"
    content = settings_file.read_text()
    assert "sentry_dsn: SecretStr" in content, (
        "sentry settings must require the DSN as a SecretStr"
    )
    assert "class SentrySettings(AppBaseSettings)" in content
    assert 'INSTALLED_APPS += ["sentry"]' in content, (
        "sentry settings must register the sentry app"
    )
    for option in (
        "sentry_environment",
        "sentry_release",
        "sentry_traces_sample_rate",
        "sentry_profiles_sample_rate",
        "sentry_send_default_pii",
        "sentry_middleware_spans",
        "sentry_capture_logs",
    ):
        assert option in content, f"{option} missing from sentry settings"
    assert "send_default_pii=True" not in content, (
        "send_default_pii must default to False — shipping user data to Sentry "
        "has to be an explicit choice"
    )
    assert "if not IS_DEV" not in content, (
        "SentrySettings must be declared at module level so the setting "
        "collector reports it in dev as well as prod"
    )


def _assert_sentry_urls_exists(root: Path) -> None:
    urls_file = root / "urls" / "apps" / "sentry.py"
    assert urls_file.exists(), "urls/apps/sentry.py missing"
    content = urls_file.read_text()
    assert 'include("sentry.urls")' in content, (
        "sentry URLs must be wired through the decentralized urls/apps module"
    )
    assert "if DEBUG else []" in content, (
        "the /sentry-debug/ endpoint must only be mounted when DEBUG is on"
    )


def _assert_peer_settings_exist(root: Path, module: str) -> None:
    assert (root / "settings" / "apps" / f"{module}.py").exists(), (
        f"settings/apps/{module}.py missing"
    )


def _assert_peer_settings_absent(root: Path, module: str) -> None:
    assert not (root / "settings" / "apps" / f"{module}.py").exists(), (
        f"settings/apps/{module}.py should not exist"
    )


def _assert_sentry_packages_installed() -> None:
    assert PixiRunner().has_dependency("sentry-sdk"), "sentry-sdk not found"


def _assert_sentry_packages_removed() -> None:
    assert not PixiRunner().has_dependency("sentry-sdk"), "sentry-sdk not removed"


# ── Tests ──────────────────────────────────────────────────────────────────────


def test_sentry_feature_is_registered():
    """The feature must be auto-discovered and declared without input params."""
    from djdevx.providers.features import app as features_app  # noqa: F401
    from djdevx.providers.features._registry import FEATURE_REGISTRY

    assert "sentry" in FEATURE_REGISTRY.names()
    feature = FEATURE_REGISTRY.get("sentry")()
    assert feature.kind.name == "feature"
    assert feature.section == Section.FEATURES
    assert feature.install_params == [], (
        "sentry must not prompt at install time — the DSN is supplied by "
        "ddx settings secrets init"
    )
    peers = {ref.name for ref in feature.peer_pixi_packages}
    assert peers == {"celery", "celery-beat"}


def test_sentry_dsn_is_reported_as_a_secret(temp_dir):
    """``sentry_dsn`` has no class default, so the collector must ask for it."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    _install_feature("sentry")

    collector = SettingCollector(temp_dir)
    collected = collector.collect()
    secrets = {info.name: info for info in collected.secrets}
    config_vars = {info.name: info for info in collected.config_vars}

    assert "sentry_dsn" in secrets, (
        "sentry_dsn must be collected as a secret, not a plain config value"
    )
    assert not secrets["sentry_dsn"].has_class_default, (
        "sentry_dsn must have no class default, otherwise a placeholder DSN "
        "would silently drop every event"
    )
    assert not secrets["sentry_dsn"].has_dev_default, (
        "sentry_dsn must not be auto-filled in dev — the operator supplies it"
    )
    assert secrets["sentry_dsn"].dev_relevant, (
        "SentrySettings sits at module level, so the DSN is asked for in dev too"
    )
    assert "sentry_environment" in config_vars, (
        "sentry config variables must be discoverable"
    )
    assert "sentry_environment" not in secrets
    for optional in (
        "sentry_traces_sample_rate",
        "sentry_profiles_sample_rate",
        "sentry_send_default_pii",
        "sentry_capture_logs",
    ):
        assert config_vars[optional].has_class_default, (
            f"{optional} must have a class default so `ddx settings configs "
            f"init prod` does not prompt for it"
        )


def test_sentry_uses_modern_sdk_without_sentry_django(temp_dir):
    """Modern sentry-sdk only: no deprecated sentry-django dependency."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)
    _install_feature("sentry")

    assert not PixiRunner().has_dependency("sentry-django"), (
        "sentry-django is deprecated; sentry_sdk.init() replaces it"
    )
    _assert_sentry_packages_installed()


def test_sentry_install_hint_mentions_the_required_dsn(temp_dir):
    """Install prints the next step: without a DSN, Django cannot import."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    result = runner.invoke(app, ["features", "add", "sentry"])
    assert result.exit_code == 0, f"Feature install failed: {result.output}"
    assert "ddx settings secrets init dev" in result.output, (
        "install must tell the operator how to supply the required DSN"
    )


def test_sentry_after_peers(temp_dir):
    """Peers installed first, then sentry — peer settings are copied."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_task_queue("celery")
    _install_scheduler("celery-beat")
    _install_feature("sentry")

    _assert_sentry_app_exists(temp_dir)
    _assert_sentry_settings_exists(temp_dir)
    _assert_sentry_urls_exists(temp_dir)
    _assert_peer_settings_exist(temp_dir, "sentry_celery")
    _assert_peer_settings_exist(temp_dir, "sentry_celery_beat")
    _assert_sentry_packages_installed()
    assert ProjectTracking().is_installed(Section.FEATURES, "sentry"), (
        "sentry not tracked after install"
    )

    celery_settings = (temp_dir / "settings" / "apps" / "sentry_celery.py").read_text()
    assert "SENTRY_CELERY_PROPAGATE_TRACES" in celery_settings
    assert "SENTRY_CELERY_MONITOR_BEAT_TASKS: bool" not in celery_settings, (
        "monitor_beat_tasks belongs to the celery-beat peer, not the celery peer"
    )
    beat_settings = (
        temp_dir / "settings" / "apps" / "sentry_celery_beat.py"
    ).read_text()
    assert "SENTRY_CELERY_MONITOR_BEAT_TASKS" in beat_settings

    _remove_feature("sentry")

    assert not (temp_dir / "sentry").exists(), "sentry directory not removed"
    assert not (temp_dir / "settings" / "apps" / "sentry.py").exists(), (
        "sentry settings not removed"
    )
    assert not (temp_dir / "urls" / "apps" / "sentry.py").exists(), (
        "sentry urls not removed"
    )
    _assert_peer_settings_absent(temp_dir, "sentry_celery")
    _assert_peer_settings_absent(temp_dir, "sentry_celery_beat")
    _assert_sentry_packages_removed()
    assert not ProjectTracking().is_installed(Section.FEATURES, "sentry"), (
        "sentry still tracked after removal"
    )
    assert ProjectTracking().is_installed(Section.TASK_QUEUE, "celery"), (
        "celery tracking lost after sentry removal"
    )


def test_sentry_before_peers(temp_dir):
    """Sentry installed first, then peers — each peer add pulls its settings."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_feature("sentry")
    _assert_peer_settings_absent(temp_dir, "sentry_celery")
    _assert_peer_settings_absent(temp_dir, "sentry_celery_beat")
    _assert_sentry_app_exists(temp_dir)

    _install_task_queue("celery")
    _assert_peer_settings_exist(temp_dir, "sentry_celery")
    _assert_peer_settings_absent(temp_dir, "sentry_celery_beat")

    _install_scheduler("celery-beat")
    _assert_peer_settings_exist(temp_dir, "sentry_celery_beat")
    _assert_sentry_settings_exists(temp_dir)


def test_sentry_peer_remove(temp_dir):
    """Removing a peer while sentry is installed drops only that peer file."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_task_queue("celery")
    _install_feature("sentry")
    _assert_peer_settings_exist(temp_dir, "sentry_celery")

    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "celery"
        result = runner.invoke(app, ["task-queue", "remove"])

    assert result.exit_code == 0, f"Task queue remove failed: {result.output}"
    _assert_peer_settings_absent(temp_dir, "sentry_celery")
    _assert_sentry_settings_exists(temp_dir)
    _assert_sentry_app_exists(temp_dir)


def test_sentry_remove(temp_dir):
    """Full sentry removal cleans up everything it added."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_feature("sentry")
    _assert_sentry_app_exists(temp_dir)

    _remove_feature("sentry")

    assert not (temp_dir / "sentry").exists(), "sentry directory not removed"
    assert not (temp_dir / "settings" / "apps" / "sentry.py").exists()
    assert not (temp_dir / "urls" / "apps" / "sentry.py").exists()
    _assert_sentry_packages_removed()
    assert not ProjectTracking().is_installed(Section.FEATURES, "sentry")


def test_sentry_secret_is_not_managed_by_the_feature(temp_dir):
    """Removal must not delete an operator-supplied DSN.

    The DSN is entered by hand, not generated by the feature, so deleting it on
    removal would destroy a value the project still needs if sentry is
    reinstalled.
    """
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_feature("sentry")
    secrets_dir = temp_dir / ".secrets"
    secrets_dir.mkdir(exist_ok=True)
    dsn_file = secrets_dir / "sentry_dsn"
    dsn_file.write_text("https://public@example.ingest.sentry.io/1\n")

    _remove_feature("sentry")

    assert dsn_file.exists(), (
        "the user-supplied .secrets/sentry_dsn must survive feature removal"
    )


def test_sentry_settings_template_declares_the_app(temp_dir):
    """The settings template must not be Jinja — nothing to render."""
    source = _template_path(
        "providers/features/sentry/templates/settings/apps/sentry.py"
    )
    assert source.exists()
    dest = TemplateManager().copy_template(source_file=source, dest_dir=temp_dir)
    content = dest.read_text()
    assert "{{" not in content and "{%" not in content, (
        "the sentry settings template has no template variables and must be a "
        "plain .py file"
    )
