"""Tests for OtelCollectorService and OpenObserveService — pixi-native OTel stack."""

from pathlib import Path
from unittest.mock import patch

from djdevx.providers.features.otel.collector_config import build_collector_config
from djdevx.services.otel import OpenObserveService, OtelCollectorService

EXAMPLE_PASSWORD = "ZoAdmin123!"


def test_build_collector_config_disables_prometheus_service_telemetry():
    rendered = build_collector_config(project_name="demo")
    assert "telemetry:" in rendered
    assert "level: none" in rendered
    assert "readers: []" in rendered


def test_devcontainer_collector_template_matches_telemetry_fix():
    repo_root = Path(__file__).resolve().parents[2]
    template = (
        repo_root
        / "djdevx"
        / "providers"
        / "features"
        / "otel"
        / "templates"
        / ".devcontainer"
        / "otel-collector-config.yaml.j2"
    )
    content = template.read_text()
    assert "telemetry:" in content
    assert "level: none" in content
    assert "readers: []" in content


def test_openobserve_up_launches_binary_with_env_not_flags(tmp_path):
    binary = tmp_path / ".pixi" / "devdata" / "bin" / "openobserve"
    binary.parent.mkdir(parents=True)
    binary.write_text("")
    service = OpenObserveService(project_root=tmp_path)
    service.binary_path = binary

    with (
        patch("djdevx.services.otel.subprocess.Popen") as popen,
        patch("djdevx.services.otel.wait_for_port", return_value=True),
    ):
        service.up()

    popen.assert_called_once()
    kwargs = popen.call_args.kwargs
    assert popen.call_args.args[0] == [str(binary)]
    assert "--local-mode" not in popen.call_args.args[0]
    env = kwargs["env"]
    assert env["ZO_ROOT_USER_EMAIL"] == "admin@example.com"
    assert env["ZO_ROOT_USER_PASSWORD"] == EXAMPLE_PASSWORD
    assert env["ZO_HTTP_PORT"] == str(service.port)
    assert env["ZO_GRPC_PORT"] == str(service.port + 1)
    assert env["ZO_DATA_DIR"] == str(service.data_dir)
    assert env["ZO_LOCAL_MODE"] == "true"


def test_openobserve_username_uses_default_email(tmp_path):
    service = OpenObserveService(project_root=tmp_path)
    assert service.username == "admin@example.com"
    assert service._root_user_email() == "admin@example.com"


def test_openobserve_username_respects_secret(tmp_path):
    secrets = tmp_path / ".secrets"
    secrets.mkdir()
    (secrets / "openobserve_email").write_text("dev@example.com")
    service = OpenObserveService(project_root=tmp_path)
    assert service.username == "dev@example.com"
    assert service._root_user_email() == "dev@example.com"


def test_collector_disables_builtin_prometheus_reader_for_dev():
    rendered = build_collector_config(
        project_name="demo",
        otlp_endpoint="0.0.0.0:54199",
        openobserve_base_url="http://localhost:5080/api/default",
    )
    assert "endpoint: 0.0.0.0:54199" in rendered
    assert "level: none" in rendered
    assert "readers: []" in rendered


def test_collector_config_uses_persisted_openobserve_port_when_not_up(tmp_path):
    """Collector must target the persisted OpenObserve port + /api/default.

    Regression: ``ddx dev up`` starts the collector before OpenObserve, so
    ``is_up()`` is False at config-write time and the config fell back to the
    hardcoded default ``http://localhost:5080``, sending telemetry to a dead
    port. The persisted port must be used regardless of readiness.
    """
    collector = OtelCollectorService(project_root=tmp_path)
    observe = OpenObserveService(project_root=tmp_path)
    observe_port = observe.port

    with patch(
        "djdevx.services.registry.resolve_openobserve_dev_service",
        return_value=observe,
    ):
        collector._ensure_config()

    config = collector.config_path.read_text()
    assert f"endpoint: http://localhost:{observe_port}/api/default" in config


def test_discover_openobserve_base_includes_api_default(tmp_path):
    collector = OtelCollectorService(project_root=tmp_path)
    observe = OpenObserveService(project_root=tmp_path)
    observe_port = observe.port

    with patch(
        "djdevx.services.registry.resolve_openobserve_dev_service",
        return_value=observe,
    ):
        assert (
            collector._discover_openobserve_base()
            == f"http://localhost:{observe_port}/api/default"
        )
