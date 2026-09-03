"""Unit tests for DockerComposePlugin imports and DeployInputs."""

import yaml

from djdevx.deployment.docker_compose import (
    DeployInputs,
    DockerComposePlugin,
    _OVERLAY_STUB,
)
from djdevx.utils.project.setting_collector import (
    CollectedSettings,
    ConfigVarInfo,
    SecretInfo,
)


class TestImports:
    """Verify that all required classes can be imported from the correct paths."""

    def test_import_deploy_inputs(self) -> None:
        assert DeployInputs is not None

    def test_import_docker_compose_plugin(self) -> None:
        assert DockerComposePlugin is not None

    def test_import_overlay_stub(self) -> None:
        assert isinstance(_OVERLAY_STUB, str)

    def test_import_collected_settings(self) -> None:
        assert CollectedSettings is not None

    def test_import_config_var_info(self) -> None:
        assert ConfigVarInfo is not None

    def test_import_secret_info(self) -> None:
        assert SecretInfo is not None


class TestDockerComposePlugin:
    """Tests for DockerComposePlugin class."""

    def test_plugin_name(self) -> None:
        assert DockerComposePlugin.name == "Docker Compose"

    def test_plugin_has_generate_params(self) -> None:
        assert len(DockerComposePlugin.generate_params) > 0

    def test_generate_params_names(self) -> None:
        param_names = [p.name for p in DockerComposePlugin.generate_params]
        assert "domain" in param_names
        assert "traefik_email" in param_names


class TestDeployInputs:
    """Tests for DeployInputs dataclass."""

    def test_create_with_required_fields(self) -> None:
        inputs = DeployInputs(traefik_email="test@example.com")
        assert inputs.traefik_email == "test@example.com"
        assert inputs.cloudflare_api_token is None

    def test_create_with_all_fields(self) -> None:
        inputs = DeployInputs(
            traefik_email="test@example.com",
            cloudflare_api_token="cf-token-123",
        )
        assert inputs.traefik_email == "test@example.com"
        assert inputs.cloudflare_api_token == "cf-token-123"

    def test_validate_domain(self) -> None:
        assert DeployInputs._validate_domain("example.com") is True
        assert DeployInputs._validate_domain("sub.example.com") is True
        assert DeployInputs._validate_domain("not-a-domain") is False

    def test_validate_email(self) -> None:
        assert DeployInputs._validate_email("test@example.com") is True
        assert DeployInputs._validate_email("invalid") is False
        assert DeployInputs._validate_email("@example.com") is False


class TestBaseCompose:
    """Tests for the generated production base compose manifest."""

    def _build(self) -> dict:
        manifest = DockerComposePlugin._build_base_compose(CollectedSettings())
        data = yaml.safe_load(manifest)
        return data["services"]["web"]

    def test_has_env_file(self) -> None:
        assert self._build()["env_file"] == [".env"]

    def test_has_healthcheck(self) -> None:
        healthcheck = self._build()["healthcheck"]
        assert "".join(healthcheck["test"]).startswith("CMD")
        assert "urlopen('http://localhost:8000/health')" in "".join(healthcheck["test"])
        assert healthcheck["interval"] == "30s"
        assert healthcheck["timeout"] == "5s"
        assert healthcheck["retries"] == 3

    def test_has_secure_traefik_routing_labels(self) -> None:
        labels = self._build()["labels"]
        assert "traefik.http.routers.web.entrypoints=websecure" in labels
        assert "traefik.http.routers.web.tls.certresolver=letsencrypt" in labels
