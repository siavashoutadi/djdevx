"""Tests for OpenTelemetry feature functionality."""

import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from djdevx.main import app
from djdevx.utils.project.pixi_runner import PixiRunner
from djdevx.utils.tracking import ProjectTracking, Section
from tests.test_helpers import create_test_django_project

runner = CliRunner()

COLLECTOR_CONTRIB_TAG = "otel/opentelemetry-collector-contrib:0.159.0"
OPENOBSERVE_TAG = "public.ecr.aws/zinclabs/openobserve:v0.92.2"


def _install_feature(name: str) -> None:
    result = runner.invoke(app, ["features", "add", name])
    assert result.exit_code == 0, f"Feature install failed: {result.output}"


def _install_database(name: str) -> None:
    result = runner.invoke(app, ["database", "add", name])
    assert result.exit_code == 0, f"Database install failed: {result.output}"


def _install_cache(name: str) -> None:
    result = runner.invoke(app, ["cache", "add", name])
    assert result.exit_code == 0, f"Cache install failed: {result.output}"


def _remove_database(name: str) -> None:
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = name
        result = runner.invoke(app, ["database", "remove"])
    assert result.exit_code == 0, f"Database remove failed: {result.output}"


def _remove_cache(name: str) -> None:
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = name
        result = runner.invoke(app, ["cache", "remove"])
    assert result.exit_code == 0, f"Cache remove failed: {result.output}"


def _assert_otel_app_exists(root: Path) -> None:
    assert (root / "otel" / "__init__.py").exists(), "otel/__init__.py missing"
    assert (root / "otel" / "apps.py").exists(), "otel/apps.py missing"
    assert (root / "otel" / "core.py").exists(), "otel/core.py missing"
    assert (root / "otel" / "setup.py").exists(), "otel/setup.py missing"
    for plugin in ("postgres.py", "redis.py"):
        assert (root / "otel" / "plugins" / plugin).exists(), (
            f"otel/plugins/{plugin} missing"
        )
    init_content = (root / "otel" / "__init__.py").read_text()
    assert "setup_otel()" not in init_content, "otel/__init__.py must not run setup"
    assert "from otel.setup import setup_otel" not in init_content, (
        "otel/__init__.py must not import setup"
    )
    setup_content = (root / "otel" / "setup.py").read_text()
    assert "pkgutil.iter_modules" in setup_content, (
        "otel/setup.py must discover plugins"
    )


def _assert_otel_settings_exists(root: Path) -> None:
    settings_file = root / "settings" / "apps" / "otel.py"
    assert settings_file.exists(), "settings/apps/otel.py missing"
    content = settings_file.read_text()
    assert "INSTALLED_APPS" in content, "otel settings missing INSTALLED_APPS"
    assert "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT" in content, (
        "otel settings missing metrics endpoint"
    )
    assert "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT" in content, (
        "otel settings missing logs endpoint"
    )
    assert "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT" in content, (
        "otel settings missing traces endpoint"
    )


def _assert_peer_settings_exist(root: Path, peer: str) -> None:
    settings_file = root / "settings" / "apps" / f"otel_{peer}.py"
    assert settings_file.exists(), f"settings/apps/otel_{peer}.py missing"
    content = settings_file.read_text()
    if peer == "postgres":
        assert "OTEL_PSYCOPG2_ENABLE_COMMENTER" in content
        assert "OTEL_PSYCOPG2_COMMENTER_OPTIONS" in content
        assert "False" in content, "postgres commenter must default to disabled"
        assert "OTEL_PSYCOPG2_DATABASE_SCHEME" not in content, (
            "stale database scheme setting must not be emitted"
        )
    if peer == "redis":
        assert "OTEL_REDIS_ENABLED" in content
        assert "OTEL_REDIS_REQUEST_HOOK" not in content, (
            "request hooks must not be emitted into settings"
        )


def _assert_peer_settings_absent(root: Path, peer: str) -> None:
    settings_file = root / "settings" / "apps" / f"otel_{peer}.py"
    assert not settings_file.exists(), f"settings/apps/otel_{peer}.py should not exist"


def _assert_otel_packages_installed() -> None:
    assert PixiRunner().has_dependency("opentelemetry-sdk"), (
        "opentelemetry-sdk not found"
    )
    assert PixiRunner().has_dependency("opentelemetry-instrumentation-django"), (
        "opentelemetry-instrumentation-django not found"
    )
    assert PixiRunner().has_dependency("opentelemetry-instrumentation-logging"), (
        "opentelemetry-instrumentation-logging not found"
    )
    assert PixiRunner().has_dependency("opentelemetry-exporter-otlp-proto-http"), (
        "opentelemetry-exporter-otlp-proto-http not found"
    )


def _assert_peer_packages_installed() -> None:
    assert PixiRunner().has_dependency("opentelemetry-instrumentation-psycopg2"), (
        "opentelemetry-instrumentation-psycopg2 not found"
    )
    assert PixiRunner().has_dependency("opentelemetry-instrumentation-redis"), (
        "opentelemetry-instrumentation-redis not found"
    )


def _assert_peer_packages_removed() -> None:
    assert not PixiRunner().has_dependency("opentelemetry-instrumentation-psycopg2"), (
        "opentelemetry-instrumentation-psycopg2 still present"
    )
    assert not PixiRunner().has_dependency("opentelemetry-instrumentation-redis"), (
        "opentelemetry-instrumentation-redis still present"
    )


def _assert_docker_services(root: Path) -> None:
    compose_file = root / ".devcontainer" / "docker-compose.yaml"
    assert compose_file.exists(), "docker-compose.yaml missing"
    content = compose_file.read_text()
    assert "otlp:" in content, "otlp service missing from docker-compose"
    assert COLLECTOR_CONTRIB_TAG in content, "collector image not pinned"
    assert "openobserve:" in content, "openobserve service missing from docker-compose"
    assert OPENOBSERVE_TAG in content, "openobserve image not pinned"


def _assert_docker_services_absent(root: Path) -> None:
    compose_file = root / ".devcontainer" / "docker-compose.yaml"
    if not compose_file.exists():
        return
    content = compose_file.read_text()
    assert "otlp:" not in content, "otlp service still in docker-compose"
    assert "openobserve:" not in content, "openobserve service still in docker-compose"


def _assert_collector_config(root: Path) -> None:
    config = root / ".devcontainer" / "otel-collector-config.yaml"
    assert config.exists(), "otel-collector-config.yaml missing"
    content = config.read_text()
    for signal in ("traces", "metrics", "logs"):
        assert f"    {signal}:" in content, f"{signal} pipeline missing"
    assert 'stream-name: "test_django_project-web"' in content, (
        "stream-name must be the project name with -web suffix"
    )
    assert "stream-name: django" not in content, "hardcoded stream-name must not remain"
    assert (
        'Authorization: "Basic YWRtaW5AZXhhbXBsZS5jb206Wm9BZG1pbjEyMyE="' in content
    ), "collector must use hardcoded Basic auth"
    assert "memory_limiter" in content, "memory_limiter processor missing"
    assert "  batch: {}" in content, "batch processor missing"


def _assert_collector_config_absent(root: Path) -> None:
    config = root / ".devcontainer" / "otel-collector-config.yaml"
    assert not config.exists(), "otel-collector-config.yaml should not exist"


# ── Tests ──────────────────────────────────────────────────────────────────────


def test_otel_after_peers(temp_dir):
    """Peers installed first, then otel — Push scenario.

    Note: pixi 0.73 cannot add conda packages after pypi packages in the
    lockfile (re-solve fails). So all installs happen conda-first.
    """
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_database("postgres")
    _install_cache("redis")
    _install_feature("otel")

    _assert_otel_app_exists(temp_dir)
    _assert_otel_settings_exists(temp_dir)
    _assert_peer_settings_exist(temp_dir, "postgres")
    _assert_peer_settings_exist(temp_dir, "redis")
    _assert_otel_packages_installed()
    _assert_peer_packages_installed()
    _assert_docker_services(temp_dir)
    _assert_collector_config(temp_dir)
    assert ProjectTracking().is_installed(Section.FEATURES, "otel"), (
        "otel not tracked after install"
    )

    result = runner.invoke(app, ["features", "remove", "otel"])
    assert result.exit_code == 0, f"Feature remove failed: {result.output}"

    assert not (temp_dir / "otel").exists(), "otel directory not removed"
    assert not (temp_dir / "settings" / "apps" / "otel.py").exists(), (
        "otel settings not removed"
    )
    _assert_peer_packages_removed()
    _assert_docker_services_absent(temp_dir)
    _assert_collector_config_absent(temp_dir)
    assert not ProjectTracking().is_installed(Section.FEATURES, "otel"), (
        "otel still tracked after removal"
    )
    assert ProjectTracking().is_installed(Section.DATABASE, "postgres"), (
        "postgres tracking lost after otel removal"
    )
    assert ProjectTracking().is_installed(Section.CACHE, "redis"), (
        "redis tracking lost after otel removal"
    )


def test_otel_before_peers(temp_dir):
    """Otel installed first, then peers — Push scenario.

    Installs otel before any peer, then adds postgres and redis afterwards.
    Each peer add must pull in otel's peer templates and packages.
    """
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_feature("otel")
    assert not (temp_dir / "otel" / "plugins" / "postgres.py").exists(), (
        "postgres plugin must not exist before postgres is installed"
    )
    assert not (temp_dir / "otel" / "plugins" / "redis.py").exists(), (
        "redis plugin must not exist before redis is installed"
    )

    _install_database("postgres")
    _install_cache("redis")

    _assert_otel_app_exists(temp_dir)
    _assert_otel_settings_exists(temp_dir)
    _assert_peer_settings_exist(temp_dir, "postgres")
    _assert_peer_settings_exist(temp_dir, "redis")
    _assert_otel_packages_installed()
    _assert_peer_packages_installed()


def test_otel_remove(temp_dir):
    """Full otel removal cleans everything."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_database("postgres")
    _install_cache("redis")
    _install_feature("otel")

    result = runner.invoke(app, ["features", "remove", "otel"])
    assert result.exit_code == 0, f"Feature remove failed: {result.output}"

    assert not (temp_dir / "otel").exists(), "otel directory not removed"
    assert not (temp_dir / "settings" / "apps" / "otel.py").exists(), (
        "otel settings not removed"
    )
    assert not PixiRunner().has_dependency("opentelemetry-sdk"), (
        "opentelemetry-sdk not removed"
    )
    assert not PixiRunner().has_dependency("opentelemetry-instrumentation-django"), (
        "opentelemetry-instrumentation-django not removed"
    )
    _assert_peer_packages_removed()
    _assert_docker_services_absent(temp_dir)
    _assert_collector_config_absent(temp_dir)
    assert not ProjectTracking().is_installed(Section.FEATURES, "otel"), (
        "otel still tracked"
    )
    assert ProjectTracking().is_installed(Section.DATABASE, "postgres"), (
        "postgres tracking lost"
    )
    assert ProjectTracking().is_installed(Section.CACHE, "redis"), "redis tracking lost"


def test_peer_remove_with_otel(temp_dir):
    """Removing peers while otel is installed."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_database("postgres")
    _install_cache("redis")
    _install_feature("otel")

    _remove_database("postgres")
    _assert_peer_settings_absent(temp_dir, "postgres")
    assert not PixiRunner().has_dependency("opentelemetry-instrumentation-psycopg2"), (
        "psycopg2 instrumentation not removed"
    )
    _assert_peer_settings_exist(temp_dir, "redis")
    _assert_otel_settings_exists(temp_dir)

    _remove_cache("redis")
    _assert_peer_settings_absent(temp_dir, "redis")
    assert not PixiRunner().has_dependency("opentelemetry-instrumentation-redis"), (
        "redis instrumentation not removed"
    )
    _assert_peer_settings_absent(temp_dir, "postgres")
    _assert_otel_settings_exists(temp_dir)


def test_peer_remove_without_otel(temp_dir):
    """Normal peer removal when otel is not installed."""
    create_test_django_project(temp_dir, runner)
    os.chdir(temp_dir)

    _install_database("postgres")
    _install_cache("redis")

    _remove_database("postgres")

    assert not (temp_dir / "settings" / "apps" / "otel_postgres.py").exists(), (
        "otel_postgres.py should not exist"
    )
    assert not (temp_dir / "settings" / "apps" / "otel_redis.py").exists(), (
        "otel_redis.py should not exist"
    )
    assert not ProjectTracking().is_installed(Section.FEATURES, "otel"), (
        "otel should not be tracked"
    )
    assert ProjectTracking().is_installed(Section.CACHE, "redis"), "redis tracking lost"
