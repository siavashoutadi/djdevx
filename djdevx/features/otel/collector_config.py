"""Render the OpenTelemetry collector config into both dev and deploy contexts.

A single source of truth so the collector config is identical whether it's
written into the devcontainer's ``.devcontainer/`` directory or into the
pixi-native data dir (``.pixi/devdata/otel/``), and into the production compose
when the OTel feature is deployed.
"""

from typing import Any

import yaml

# Default raw OpenObserve instance credentials. These are the stock
# OpenObserve bootstrap credentials used by the devcontainer image.
OPENOBSERVE_DEFAULT_EMAIL = "admin@example.com"
OPENOBSERVE_DEFAULT_PASSWORD = "ZoAdmin123!"


def build_collector_config(
    *,
    project_name: str,
    otlp_endpoint: str = "0.0.0.0:4318",
    openobserve_base_url: str = "http://openobserve:5080",
    openobserve_authorization: str = "Basic YWRtaW5AZXhhbXBsZS5jb206Wm9BZG1pbjEyMyE=",
    stream_name: str | None = None,
    include_shapes: tuple[str, ...] = ("traces", "metrics", "logs"),
) -> str:
    """Return the rendered otel collector YAML config.

    Args:
        project_name: Project name used to build the default stream name.
        otlp_endpoint: Host:port the collector receives OTLP/HTTP on.
        openobserve_base_url: Base URL of the OpenObserve instance to export to.
        openobserve_authorization: Value for the collector's ``Authorization``
            header (used for OTLP auth).
        stream_name: Stream name override; defaults to ``<project>-web``.
        include_shapes: Which pipelines to emit.
    """
    if stream_name is None:
        stream_name = f"{project_name}-web"

    receivers = {
        "otlp": {
            "protocols": {
                "http": {"endpoint": otlp_endpoint},
            },
        },
    }

    processors = {
        "memory_limiter": {
            "check_interval": "1s",
            "limit_percentage": 80,
            "spike_limit_percentage": 25,
        },
        "batch": {},
    }

    exporters = {
        "otlphttp/openobserve": {
            "endpoint": openobserve_base_url,
            "headers": {
                "Authorization": openobserve_authorization,
                "stream-name": stream_name,
            },
        },
    }

    pipelines = {
        signal: {
            "receivers": ["otlp"],
            "processors": ["memory_limiter", "batch"],
            "exporters": ["otlphttp/openobserve"],
        }
        for signal in include_shapes
    }

    config: dict[str, Any] = {
        "receivers": receivers,
        "processors": processors,
        "exporters": exporters,
        "service": {"pipelines": pipelines},
    }
    return yaml.dump(config, default_flow_style=False, sort_keys=False)
