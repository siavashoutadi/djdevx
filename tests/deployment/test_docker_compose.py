"""Tests for DockerComposePlugin and DeployInputs."""

from pathlib import Path
from unittest.mock import patch

import yaml

from djdevx.deployment.docker_compose import (
    DeployInputs,
    DockerComposePlugin,
    _OVERLAY_STUB,
)
from djdevx.utils.django.setting_collector import (
    CollectedSettings,
    ConfigVarInfo,
    SecretInfo,
)


# ---------------------------------------------------------------------------
# DeployInputs
# ---------------------------------------------------------------------------


class TestDeployInputs:
    def test_validate_domain_valid(self):
        assert DeployInputs._validate_domain("example.com") is True
        assert DeployInputs._validate_domain("sub.example.com") is True
        assert DeployInputs._validate_domain("my-app.example.co.uk") is True

    def test_validate_domain_invalid(self):
        assert DeployInputs._validate_domain("") is False
        assert DeployInputs._validate_domain("not_a_domain") is False
        assert DeployInputs._validate_domain("example") is False

    def test_validate_email_valid(self):
        assert DeployInputs._validate_email("admin@example.com") is True
        assert DeployInputs._validate_email("user+tag@example.co.uk") is True

    def test_validate_email_invalid(self):
        assert DeployInputs._validate_email("") is False
        assert DeployInputs._validate_email("not-an-email") is False
        assert DeployInputs._validate_email("@example.com") is False
        assert DeployInputs._validate_email("user@") is False

    def test_load_from_env_missing_file(self, temp_dir: Path):
        assert DeployInputs.load_from_env(temp_dir / "nonexistent") is None

    def test_load_from_env_with_email(self, temp_dir: Path):
        env_file = temp_dir / ".env"
        env_file.write_text("TRAEFIK_EMAIL=admin@test.com\n")
        inputs = DeployInputs.load_from_env(env_file)
        assert inputs is not None
        assert inputs.traefik_email == "admin@test.com"
        assert inputs.cloudflare_api_token is None

    def test_load_from_env_with_token(self, temp_dir: Path):
        env_file = temp_dir / ".env"
        env_file.write_text("TRAEFIK_EMAIL=admin@test.com\nCF_DNS_API_TOKEN=abc123\n")
        inputs = DeployInputs.load_from_env(env_file)
        assert inputs is not None
        assert inputs.traefik_email == "admin@test.com"
        assert inputs.cloudflare_api_token == "abc123"

    def test_load_from_env_missing_email(self, temp_dir: Path):
        env_file = temp_dir / ".env"
        env_file.write_text("CF_DNS_API_TOKEN=abc123\n")
        assert DeployInputs.load_from_env(env_file) is None

    def test_write_to_env(self, temp_dir: Path):
        inputs = DeployInputs(
            traefik_email="admin@test.com", cloudflare_api_token="abc123"
        )
        env_file = temp_dir / ".env"
        inputs.write_to_env(env_file)
        content = env_file.read_text()
        assert "TRAEFIK_EMAIL=admin@test.com" in content
        assert "CF_DNS_API_TOKEN=abc123" in content

    def test_write_to_env_creates_parent_dirs(self, temp_dir: Path):
        inputs = DeployInputs(traefik_email="admin@test.com")
        env_file = temp_dir / "sub" / ".env"
        inputs.write_to_env(env_file)
        assert env_file.exists()
        assert "TRAEFIK_EMAIL=admin@test.com" in env_file.read_text()

    def test_write_to_env_no_token(self, temp_dir: Path):
        inputs = DeployInputs(traefik_email="admin@test.com")
        env_file = temp_dir / ".env"
        inputs.write_to_env(env_file)
        assert "CF_DNS_API_TOKEN" not in env_file.read_text()


# ---------------------------------------------------------------------------
# DockerComposePlugin — manifest builders
# ---------------------------------------------------------------------------


class TestDockerComposeBuildTraefikCompose:
    def test_without_cloudflare(self):
        inputs = DeployInputs(traefik_email="admin@test.com")
        result = DockerComposePlugin._build_traefik_compose(inputs)
        parsed = yaml.safe_load(result)
        assert parsed is not None
        assert "services" in parsed
        assert "traefik" in parsed["services"]
        traefik = parsed["services"]["traefik"]
        assert traefik["image"] == "traefik:v3.3"
        # Should use TLS challenge (no DNS challenge config)
        cmd = " ".join(traefik["command"])
        assert "tlschallenge=true" in cmd
        assert "dnschallenge" not in cmd
        assert "CF_DNS_API_TOKEN" not in str(traefik.get("environment", {}))
        assert traefik["restart"] == "unless-stopped"

    def test_with_cloudflare(self):
        inputs = DeployInputs(
            traefik_email="admin@test.com", cloudflare_api_token="abc123"
        )
        result = DockerComposePlugin._build_traefik_compose(inputs)
        parsed = yaml.safe_load(result)
        assert parsed is not None
        traefik = parsed["services"]["traefik"]
        cmd = " ".join(traefik["command"])
        assert "dnschallenge=true" in cmd
        assert "dnschallenge.provider=cloudflare" in cmd
        assert "tlschallenge=true" not in cmd
        assert traefik["environment"]["CF_DNS_API_TOKEN"] == "${CF_DNS_API_TOKEN}"


class TestDockerComposeBuildBaseCompose:
    def test_no_secrets(self):
        settings = CollectedSettings(secrets=[], config_vars=[])
        result = DockerComposePlugin._build_base_compose(settings)
        parsed = yaml.safe_load(result)
        assert parsed is not None
        assert "services" in parsed
        assert "web" in parsed["services"]
        assert "secrets" not in parsed
        assert parsed["networks"]["traefik-public"]["external"] is True

    def test_with_secrets(self):
        settings = CollectedSettings(
            secrets=[
                SecretInfo(name="DATABASE_PASSWORD", source_file=Path("test.py")),
                SecretInfo(name="SECRET_KEY", source_file=Path("test.py")),
            ],
            config_vars=[],
        )
        result = DockerComposePlugin._build_base_compose(settings)
        parsed = yaml.safe_load(result)
        assert parsed is not None
        assert "secrets" in parsed
        assert "DATABASE_PASSWORD" in parsed["secrets"]
        assert parsed["secrets"]["DATABASE_PASSWORD"] == {
            "file": ".secrets/DATABASE_PASSWORD"
        }
        assert "SECRET_KEY" in parsed["secrets"]
        assert "web" in parsed["services"]
        assert parsed["services"]["web"]["secrets"] == [
            "DATABASE_PASSWORD",
            "SECRET_KEY",
        ]

    def test_has_traefik_labels(self):
        settings = CollectedSettings(secrets=[], config_vars=[])
        result = DockerComposePlugin._build_base_compose(settings)
        parsed = yaml.safe_load(result)
        labels = parsed["services"]["web"]["labels"]
        assert "traefik.enable=true" in labels
        assert "traefik.http.routers.web.rule=Host(`$DOMAIN`)" in labels

    def test_image_default(self):
        settings = CollectedSettings(secrets=[], config_vars=[])
        result = DockerComposePlugin._build_base_compose(settings)
        parsed = yaml.safe_load(result)
        assert parsed["services"]["web"]["image"] == "${IMAGE:-your-app:latest}"


# ---------------------------------------------------------------------------
# DockerComposePlugin — generate (with mocks)
# ---------------------------------------------------------------------------


class TestDockerComposeGenerate:
    def _make_mock_inputs(self) -> DeployInputs:
        return DeployInputs(traefik_email="admin@test.com")

    @patch.object(
        DockerComposePlugin, "_build_app_env", return_value="DOMAIN=example.com\n"
    )
    @patch.object(DockerComposePlugin, "_resolve_secret_value", return_value=None)
    @patch.object(DockerComposePlugin, "_read_env_prod", return_value={})
    @patch.object(DockerComposePlugin, "_collect_settings")
    @patch.object(DockerComposePlugin, "_resolve_deploy_config")
    def test_generate_creates_all_files(
        self,
        mock_resolve_deploy,
        mock_collect_settings,
        mock_read_env,
        mock_resolve_secret,
        mock_build_env,
        temp_dir: Path,
    ):
        mock_collect_settings.return_value = CollectedSettings(
            secrets=[], config_vars=[]
        )
        mock_resolve_deploy.return_value = self._make_mock_inputs()

        plugin = DockerComposePlugin()
        plugin.generate(
            temp_dir,
            domain="example.com",
            traefik_email="admin@test.com",
            cloudflare_token="",
        )

        assert (temp_dir / "traefik" / "docker-compose.yml").exists()
        assert (temp_dir / "app" / "docker-compose.base.yml").exists()
        assert (temp_dir / "app" / "docker-compose.prod.yml").exists()
        assert (temp_dir / "app" / ".env").exists()
        assert (temp_dir / "app" / ".env").read_text().strip() == "DOMAIN=example.com"
        assert (temp_dir / "traefik" / ".env").exists()
        assert (
            temp_dir / "traefik" / ".env"
        ).read_text().strip() == "TRAEFIK_EMAIL=admin@test.com"

    @patch.object(
        DockerComposePlugin, "_build_app_env", return_value="DOMAIN=example.com\n"
    )
    @patch.object(DockerComposePlugin, "_resolve_secret_value", return_value=None)
    @patch.object(DockerComposePlugin, "_read_env_prod", return_value={})
    @patch.object(DockerComposePlugin, "_collect_settings")
    @patch.object(DockerComposePlugin, "_resolve_deploy_config")
    def test_generate_with_secrets(
        self,
        mock_resolve_deploy,
        mock_collect_settings,
        mock_read_env,
        mock_resolve_secret,
        mock_build_env,
        temp_dir: Path,
    ):
        mock_collect_settings.return_value = CollectedSettings(
            secrets=[
                SecretInfo(name="MY_SECRET", source_file=Path("test.py")),
            ],
            config_vars=[],
        )
        mock_resolve_deploy.return_value = self._make_mock_inputs()
        mock_resolve_secret.return_value = "super-secret-value"

        plugin = DockerComposePlugin()
        plugin.generate(
            temp_dir,
            domain="example.com",
            traefik_email="admin@test.com",
            cloudflare_token="",
        )

        secret_file = temp_dir / "app" / ".secrets" / "MY_SECRET"
        assert secret_file.exists()
        assert secret_file.read_text().strip() == "super-secret-value"

    @patch.object(
        DockerComposePlugin, "_build_app_env", return_value="DOMAIN=example.com\n"
    )
    @patch.object(DockerComposePlugin, "_resolve_secret_value", return_value=None)
    @patch.object(DockerComposePlugin, "_read_env_prod", return_value={})
    @patch.object(DockerComposePlugin, "_collect_settings")
    @patch.object(DockerComposePlugin, "_resolve_deploy_config")
    def test_generate_base_compose_is_valid_yaml(
        self,
        mock_resolve_deploy,
        mock_collect_settings,
        mock_read_env,
        mock_resolve_secret,
        mock_build_env,
        temp_dir: Path,
    ):
        mock_collect_settings.return_value = CollectedSettings(
            secrets=[], config_vars=[]
        )
        mock_resolve_deploy.return_value = self._make_mock_inputs()

        plugin = DockerComposePlugin()
        plugin.generate(
            temp_dir,
            domain="example.com",
            traefik_email="admin@test.com",
            cloudflare_token="",
        )

        base_yml = temp_dir / "app" / "docker-compose.base.yml"
        parsed = yaml.safe_load(base_yml.read_text())
        assert parsed is not None
        assert "services" in parsed

    @patch.object(
        DockerComposePlugin, "_build_app_env", return_value="DOMAIN=example.com\n"
    )
    @patch.object(DockerComposePlugin, "_resolve_secret_value", return_value=None)
    @patch.object(DockerComposePlugin, "_read_env_prod", return_value={})
    @patch.object(DockerComposePlugin, "_collect_settings")
    @patch.object(DockerComposePlugin, "_resolve_deploy_config")
    def test_overlay_stub_is_written(
        self,
        mock_resolve_deploy,
        mock_collect_settings,
        mock_read_env,
        mock_resolve_secret,
        mock_build_env,
        temp_dir: Path,
    ):
        mock_collect_settings.return_value = CollectedSettings(
            secrets=[], config_vars=[]
        )
        mock_resolve_deploy.return_value = self._make_mock_inputs()

        plugin = DockerComposePlugin()
        plugin.generate(
            temp_dir,
            domain="example.com",
            traefik_email="admin@test.com",
            cloudflare_token="",
        )

        overlay = temp_dir / "app" / "docker-compose.prod.yml"
        assert overlay.exists()
        assert overlay.read_text() == _OVERLAY_STUB

    @patch.object(
        DockerComposePlugin, "_build_app_env", return_value="DOMAIN=example.com\n"
    )
    @patch.object(DockerComposePlugin, "_resolve_secret_value", return_value=None)
    @patch.object(DockerComposePlugin, "_read_env_prod", return_value={})
    @patch.object(DockerComposePlugin, "_collect_settings")
    @patch.object(DockerComposePlugin, "_resolve_deploy_config")
    def test_overlay_stub_not_overwritten(
        self,
        mock_resolve_deploy,
        mock_collect_settings,
        mock_read_env,
        mock_resolve_secret,
        mock_build_env,
        temp_dir: Path,
    ):
        """verify that the overlay stub is never overwritten after creation."""
        mock_collect_settings.return_value = CollectedSettings(
            secrets=[], config_vars=[]
        )
        mock_resolve_deploy.return_value = self._make_mock_inputs()

        plugin = DockerComposePlugin()
        # First generate
        plugin.generate(
            temp_dir,
            domain="example.com",
            traefik_email="admin@test.com",
            cloudflare_token="",
        )
        # Modify the overlay
        overlay = temp_dir / "app" / "docker-compose.prod.yml"
        overlay.write_text("# custom user content\n")
        # Second generate — should NOT overwrite overlay
        plugin.generate(
            temp_dir,
            domain="different.com",
            traefik_email="other@test.com",
            cloudflare_token="secret",
        )
        assert overlay.read_text() == "# custom user content\n"


# ---------------------------------------------------------------------------
# DockerComposePlugin — verify
# ---------------------------------------------------------------------------


class TestDockerComposeVerify:
    @patch.object(DockerComposePlugin, "_build_app_env", return_value=None)
    @patch.object(DockerComposePlugin, "_read_env_prod", return_value={})
    @patch.object(DockerComposePlugin, "_collect_settings")
    def test_verify_fails_when_files_missing(
        self,
        mock_collect_settings,
        mock_read_env,
        mock_build_env,
        temp_dir: Path,
    ):
        mock_collect_settings.return_value = CollectedSettings(
            secrets=[], config_vars=[]
        )

        plugin = DockerComposePlugin()
        result = plugin.verify(temp_dir)
        assert result is False

    @patch.object(
        DockerComposePlugin, "_build_app_env", return_value="DOMAIN=example.com\n"
    )
    @patch.object(
        DockerComposePlugin, "_resolve_config_value", return_value="prod_value"
    )
    @patch.object(
        DockerComposePlugin, "_resolve_secret_value", return_value="some-value"
    )
    @patch.object(
        DockerComposePlugin, "_read_env_prod", return_value={"DOMAIN": "example.com"}
    )
    @patch.object(DockerComposePlugin, "_collect_settings")
    @patch.object(DockerComposePlugin, "_resolve_deploy_config")
    def test_verify_passes_with_all_files(
        self,
        mock_resolve_deploy,
        mock_collect_settings,
        mock_read_env,
        mock_resolve_secret,
        mock_resolve_config,
        mock_build_env,
        temp_dir: Path,
    ):
        mock_collect_settings.return_value = CollectedSettings(
            secrets=[SecretInfo(name="TEST_SECRET", source_file=Path("test.py"))],
            config_vars=[ConfigVarInfo(name="TEST_VAR", source_file=Path("test.py"))],
        )
        mock_resolve_deploy.return_value = DeployInputs(traefik_email="admin@test.com")

        plugin = DockerComposePlugin()

        # Pre-create all the files matching mocked expectations
        (temp_dir / "traefik").mkdir(parents=True)
        (temp_dir / "traefik" / ".env").write_text("TRAEFIK_EMAIL=admin@test.com\n")
        traefik_yml = temp_dir / "traefik" / "docker-compose.yml"
        traefik_yml.write_text(
            DockerComposePlugin._build_traefik_compose(
                DeployInputs(traefik_email="admin@test.com")
            )
        )
        (temp_dir / "app").mkdir(parents=True)
        (temp_dir / "app" / "docker-compose.base.yml").write_text(
            DockerComposePlugin._build_base_compose(
                CollectedSettings(
                    secrets=[
                        SecretInfo(name="TEST_SECRET", source_file=Path("test.py"))
                    ],
                    config_vars=[],
                )
            )
        )
        (temp_dir / "app" / "docker-compose.prod.yml").write_text("test")
        (temp_dir / "app" / ".secrets").mkdir(parents=True)
        (temp_dir / "app" / ".secrets" / "TEST_SECRET").write_text("some-value")
        app_env = temp_dir / "app" / ".env"
        app_env.write_text("DOMAIN=example.com\n")

        result = plugin.verify(temp_dir)
        assert result is True
