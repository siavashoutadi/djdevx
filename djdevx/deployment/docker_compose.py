"""Docker Compose deployment plugin with Traefik ingress."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

import yaml
from dotenv import dotenv_values

import secrets

from ..settings.source import setup_readline
from ..utils.console import prompts
from ..utils.console.print import print_console
from ..utils.project.setting_collector import CollectedSettings, SettingCollector
from ..utils.project.project_structure import ProjectStructure
from ..utils.tracking import ProjectTracking, Section

from ._base import BaseDeployPlugin, DeployParam


# ---------------------------------------------------------------------------
# Helper dataclass for Traefik deployment inputs
# ---------------------------------------------------------------------------


@dataclass
class DeployInputs:
    traefik_email: str
    cloudflare_api_token: str | None = None

    @classmethod
    def load_from_env(cls, path: Path) -> Self | None:
        if not path.exists():
            return None
        values = dotenv_values(path)
        traefik_email = values.get("TRAEFIK_EMAIL")
        if not traefik_email:
            return None
        return cls(
            traefik_email=traefik_email,
            cloudflare_api_token=values.get("CF_DNS_API_TOKEN") or None,
        )

    def write_to_env(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"TRAEFIK_EMAIL={self.traefik_email}",
        ]
        if self.cloudflare_api_token:
            lines.append(f"CF_DNS_API_TOKEN={self.cloudflare_api_token}")
        path.write_text("\n".join(lines) + "\n")

    @staticmethod
    def _validate_domain(domain: str) -> bool:
        return bool(re.match(r"^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", domain))

    @staticmethod
    def _validate_email(email: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    @classmethod
    def collect(
        cls,
        traefik_email: str | None = None,
        cloudflare_api_token: str | None = None,
    ) -> Self:
        setup_readline()
        if traefik_email is None:
            while True:
                traefik_email = input("Let's Encrypt email: ").strip()
                if cls._validate_email(traefik_email):
                    break
                print_console.fail("Invalid email address. Please try again.")
        if cloudflare_api_token is None:
            result = prompts.password(
                "CF_DNS_API_TOKEN (optional, press Enter to skip)",
                default="",
            )
            cloudflare_api_token = result or None
        return cls(
            traefik_email=traefik_email,
            cloudflare_api_token=cloudflare_api_token or None,
        )


# ---------------------------------------------------------------------------
# Main plugin
# ---------------------------------------------------------------------------


class DockerComposePlugin(BaseDeployPlugin):
    """Generates Docker Compose production manifests with Traefik auto-discovery.

    Generated layout::

        deployment/docker-compose/
        \u251c\u2500\u2500 traefik/
        \u2502   \u251c\u2500\u2500 .env                    # TRAEFIK_EMAIL, CF_DNS_API_TOKEN
        \u2502   \u2514\u2500\u2500 docker-compose.yml      # Traefik reverse-proxy
        \u2514\u2500\u2500 app/
            \u251c\u2500\u2500 .env                    # config vars (copied from backend/.env.prod)
            \u251c\u2500\u2500 .secrets/<name>         # one file per secret (written by generate)
            \u251c\u2500\u2500 docker-compose.base.yml # always regenerated
            \u2514\u2500\u2500 docker-compose.prod.yml # created once, never overwritten
    """

    name: str = "Docker Compose"

    generate_params: list[DeployParam] = [
        DeployParam(
            name="domain",
            type_=str,
            help="Domain name for the deployment",
            default=None,
            prompt="Domain name:",
        ),
        DeployParam(
            name="traefik_email",
            type_=str,
            help="Email for Let's Encrypt certificates",
            default=None,
            prompt="Let's Encrypt email:",
        ),
        DeployParam(
            name="cloudflare_token",
            type_=str,
            help="CF_DNS_API_TOKEN for Cloudflare DNS challenge (optional)",
            default="",
            prompt="CF_DNS_API_TOKEN (optional, press Enter to skip)",
            hide_input=True,
        ),
    ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, output_dir: Path, step=None, **kwargs: Any) -> None:
        settings = self._collect_settings()

        traefik_email = kwargs.get("traefik_email")
        cloudflare_token = kwargs.get("cloudflare_token")
        domain = kwargs.get("domain")

        inputs = self._resolve_deploy_config(
            output_dir, traefik_email, cloudflare_token
        )
        self._write_env_traefik(output_dir, inputs)
        self._copy_app_env(output_dir, domain=domain)
        self._write_secret_files(output_dir, settings)
        self._warn_missing_configs(settings)
        self._write(
            output_dir / "app" / "docker-compose.base.yml",
            self._build_base_compose(settings),
            step=step,
        )
        self._write(
            output_dir / "traefik" / "docker-compose.yml",
            self._build_traefik_compose(inputs),
            step=step,
        )
        self._write_once(
            output_dir / "app" / "docker-compose.prod.yml", _OVERLAY_STUB, step=step
        )

    def verify(self, output_dir: Path) -> bool:
        settings = self._collect_settings()

        all_ok = True

        with print_console.step_group(
            f"Verifying {self.name} deployment in {output_dir} \u2026",
            done="All checks passed.",
        ) as step:
            # -- manifest files
            for f in ("docker-compose.base.yml", "docker-compose.prod.yml"):
                path = output_dir / "app" / f
                if path.exists():
                    step.ok(f"app/{f}")
                else:
                    step.fail(f"app/{f}  (missing \u2014 run generate first)")
                    all_ok = False

            # -- secrets
            secrets_dir = output_dir / "app" / ".secrets"
            for secret in settings.secrets:
                secret_path = secrets_dir / secret.name
                if secret_path.exists():
                    step.ok(f"{secret.name}  ({secret_path.relative_to(output_dir)})")
                elif self._resolve_secret_value(secret) is not None:
                    step.warning(
                        f"\u26a0  {secret.name}  (not written yet \u2014 run generate to create)"
                    )
                    all_ok = False
                else:
                    hint = self._hint_secrets_command()
                    step.fail(f"{secret.name}  (no value)")
                    step.info(f"Run: {hint}")
                    all_ok = False

            # -- config vars
            for cv in settings.config_vars:
                if cv.name.upper() == "DEBUG":
                    step.ok(f"{cv.name}  (hardcoded to false)")
                elif self._resolve_config_value(cv) is not None:
                    step.ok(f"{cv.name}  (resolved)")
                else:
                    hint = self._hint_configs_command()
                    step.fail(f"{cv.name}  (no value)")
                    step.info(f"Run: {hint}")
                    all_ok = False

            # -- traefik/.env (inputs)
            traefik_env = output_dir / "traefik" / ".env"
            traefik_env_ok = False
            if traefik_env.exists():
                inputs = DeployInputs.load_from_env(traefik_env)
                if inputs is not None:
                    traefik_env_ok = True
                    step.ok("traefik/.env  (current)")
                else:
                    step.fail("traefik/.env  (missing TRAEFIK_EMAIL)")
                    all_ok = False
            else:
                step.fail("traefik/.env  (missing)")
                step.info("Run: ddx deployment docker-compose generate")
                all_ok = False

            # -- drift: traefik/docker-compose.yml
            if traefik_env_ok and inputs is not None:
                traefik_yml = output_dir / "traefik" / "docker-compose.yml"
                if traefik_yml.exists():
                    expected_traefik = self._build_traefik_compose(inputs)
                    current_traefik = traefik_yml.read_text()
                    if current_traefik != expected_traefik:
                        print_console.diff(
                            current_traefik,
                            expected_traefik,
                            title_old="traefik/docker-compose.yml (current)",
                            title_new="traefik/docker-compose.yml (expected)",
                        )
                        step.info("traefik/docker-compose.yml  (drift detected)")
                        all_ok = False
                    else:
                        step.ok("traefik/docker-compose.yml  (current)")
                else:
                    step.fail(
                        "traefik/docker-compose.yml  (missing \u2014 run generate)"
                    )
                    all_ok = False

            # -- drift: app/.env
            app_env_path = output_dir / "app" / ".env"
            if app_env_path.exists():
                expected_env = self._build_app_env(output_dir)
                if expected_env is not None:
                    current_env = app_env_path.read_text()
                    if current_env != expected_env:
                        print_console.diff(
                            current_env,
                            expected_env,
                            title_old="app/.env (current)",
                            title_new="app/.env (expected)",
                        )
                        step.info("app/.env  (drift detected)")
                        all_ok = False
                    else:
                        step.ok("app/.env  (current)")
            else:
                step.fail("app/.env  (missing)")
                step.info("Run: ddx deployment docker-compose generate")
                all_ok = False

            # -- DOMAIN in app/.env
            app_env_vars = dotenv_values(app_env_path) if app_env_path.exists() else {}
            if not app_env_vars.get("DOMAIN"):
                step.fail("app/.env  (missing DOMAIN)")
                step.info("Run: ddx deployment docker-compose generate")
                all_ok = False

            # -- drift: docker-compose.base.yml
            base_yml = output_dir / "app" / "docker-compose.base.yml"
            if traefik_env_ok and inputs is not None and base_yml.exists():
                expected_yml = self._build_base_compose(settings)
                current_yml = base_yml.read_text()
                if current_yml != expected_yml:
                    print_console.diff(
                        current_yml,
                        expected_yml,
                        title_old="app/docker-compose.base.yml (current)",
                        title_new="app/docker-compose.base.yml (expected)",
                    )
                    step.info("app/docker-compose.base.yml  (drift detected)")
                    all_ok = False
                else:
                    step.ok("app/docker-compose.base.yml  (current)")
            elif not base_yml.exists():
                step.fail("app/docker-compose.base.yml  (missing \u2014 run generate)")
                all_ok = False

            if not all_ok:
                step.fail("Some checks failed. Fix the issues above before deploying.")

        return all_ok

    # ------------------------------------------------------------------
    # Settings collection + resolution (Django-specific helpers)
    # ------------------------------------------------------------------

    @staticmethod
    def _collect_settings() -> CollectedSettings:
        root = ProjectStructure().root
        collector = SettingCollector(root)
        return collector.collect()

    def _resolve_secret_value(self, secret: Any) -> str | None:
        backend_root = ProjectStructure().root
        prod_file = backend_root / ".secrets.prod" / secret.name
        if prod_file.exists():
            return prod_file.read_text().strip()
        return None

    @staticmethod
    def _hint_secrets_command() -> str:
        return "ddx settings secrets init prod"

    def _resolve_config_value(self, config_var: Any) -> str | None:
        env_prod = self._read_env_prod()
        key = config_var.name.upper()
        if key in env_prod:
            val = env_prod[key]
            if val is not None:
                return str(val)
        if config_var.prod_default is not None:
            return self._to_env_str(config_var.prod_default)
        return None

    @staticmethod
    def _hint_configs_command() -> str:
        return "ddx settings configs init prod"

    @staticmethod
    def _read_env_prod() -> dict[str, str | None]:
        backend_root = ProjectStructure().root
        env_path = backend_root / ".env.prod"
        if not env_path.exists():
            return {}
        return dotenv_values(env_path)

    # ------------------------------------------------------------------
    # Deploy config resolution
    # ------------------------------------------------------------------

    def _resolve_deploy_config(
        self,
        output_dir: Path,
        traefik_email: str | None = None,
        cloudflare_token: str | None = None,
    ) -> DeployInputs:
        env_path = output_dir / "traefik" / ".env"
        existing = DeployInputs.load_from_env(env_path)
        if existing is not None:
            return existing
        inputs = DeployInputs.collect(
            traefik_email=traefik_email,
            cloudflare_api_token=cloudflare_token,
        )
        return inputs

    @staticmethod
    def _write_env_traefik(output_dir: Path, inputs: DeployInputs) -> None:
        env_path = output_dir / "traefik" / ".env"
        if env_path.exists():
            print_console.info(f"  kept   {env_path}  (no change)")
            return
        inputs.write_to_env(env_path)
        print_console.info(f"  wrote  {env_path}")

    @staticmethod
    def _copy_app_env(output_dir: Path, domain: str | None = None) -> None:
        content = DockerComposePlugin._build_app_env(output_dir, domain=domain)
        if content is None:
            return
        app_env = output_dir / "app" / ".env"
        if app_env.exists():
            old_content = app_env.read_text()
            if old_content == content:
                print_console.info(f"  kept   {app_env}  (no change)")
                return
            print_console.diff(
                old_content,
                content,
                title_old="app/.env (current)",
                title_new="app/.env (new)",
            )
        app_env.parent.mkdir(parents=True, exist_ok=True)
        app_env.write_text(content)
        print_console.info(f"  wrote  {app_env}")

    # ------------------------------------------------------------------
    # Secret file writer
    # ------------------------------------------------------------------

    def _write_secret_files(
        self, output_dir: Path, settings: CollectedSettings
    ) -> None:
        secrets_dir = output_dir / "app" / ".secrets"
        for secret in settings.secrets:
            secret_path = secrets_dir / secret.name
            if secret_path.exists():
                print_console.info(f"  kept   {secret_path}  (no change)")
                continue

            value = self._resolve_secret_value(secret)
            if value is None:
                hint = self._hint_secrets_command()
                print_console.fail(f"  {secret.name}  (no value)")
                print_console.info(f"     Run: {hint}")
                print_console.info(f"     Or create {secret_path} manually")
                continue

            self._write(secret_path, value)

    # ------------------------------------------------------------------
    # Config var warnings
    # ------------------------------------------------------------------

    def _warn_missing_configs(self, settings: CollectedSettings) -> None:
        missing = []
        for cv in settings.config_vars:
            if cv.name.upper() == "DEBUG":
                continue
            if self._resolve_config_value(cv) is None:
                missing.append(cv.name)
        if not missing:
            return
        hint = self._hint_configs_command()
        for name in missing:
            print_console.fail(f"  {name}  (no value)")
            print_console.info(f"     Run: {hint}")

    # ------------------------------------------------------------------
    # Manifest builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_app_env(output_dir: Path, domain: str | None = None) -> str | None:
        backend_root = ProjectStructure().root
        env_prod = backend_root / ".env.prod"
        if not env_prod.exists():
            print_console.fail(f"  {env_prod} not found")
            print_console.info("     Run: ddx settings configs init prod")
            return None

        app_env = output_dir / "app" / ".env"
        existing_vars = dotenv_values(app_env) if app_env.exists() else {}

        if "DOMAIN" in existing_vars:
            domain = existing_vars["DOMAIN"]
        elif not domain:
            setup_readline()
            while not domain:
                domain = input("Domain name: ").strip()
                if not DeployInputs._validate_domain(domain):
                    print_console.fail(
                        "Invalid domain. Please try again (e.g. example.com)."
                    )
                    domain = None

        content = env_prod.read_text()
        if domain:
            content = f"DOMAIN={domain}\n{content}"
        return content

    @staticmethod
    def _build_traefik_compose(inputs: DeployInputs) -> str:
        command = [
            "--providers.docker=true",
            "--providers.docker.exposedbydefault=false",
            "--entrypoints.web.address=:80",
            "--entrypoints.websecure.address=:443",
        ]
        if inputs.cloudflare_api_token:
            command.extend(
                [
                    "--certificatesresolvers.letsencrypt.acme.dnschallenge=true",
                    "--certificatesresolvers.letsencrypt.acme.dnschallenge.provider=cloudflare",
                ]
            )
        else:
            command.append("--certificatesresolvers.letsencrypt.acme.tlschallenge=true")
        command.extend(
            [
                "--certificatesresolvers.letsencrypt.acme.email=${TRAEFIK_EMAIL}",
                "--certificatesresolvers.letsencrypt.acme.storage=/acme/acme.json",
            ]
        )

        service: dict = {
            "image": "traefik:v3.3",
            "command": command,
            "ports": ["80:80", "443:443"],
            "volumes": [
                "/var/run/docker.sock:/var/run/docker.sock:ro",
                "traefik-acme:/acme",
            ],
            "networks": ["traefik-public"],
            "restart": "unless-stopped",
        }
        if inputs.cloudflare_api_token:
            service["environment"] = {"CF_DNS_API_TOKEN": "${CF_DNS_API_TOKEN}"}

        compose: dict = {
            "services": {"traefik": service},
            "networks": {"traefik-public": {"driver": "bridge"}},
            "volumes": {"traefik-acme": None},
        }

        lines = [
            "# docker-compose.yml \u2014 Traefik reverse-proxy for Docker Compose.",
            "# Generated by ddx deploy docker-compose \u2014 edit this file to suit your setup.",
            "#",
            "# Traefik auto-discovers services via Docker labels.  Your app's base compose",
            "# already includes the required labels.",
            "#",
            "# Deploy:",
            "#   docker compose -f traefik/docker-compose.yml up -d",
            "#",
            "# Then deploy your app:",
            "#   docker compose -f app/docker-compose.base.yml -f app/docker-compose.prod.yml up -d",
            "",
        ]
        lines.append(
            yaml.dump(compose, default_flow_style=False, sort_keys=False).rstrip()
        )
        return "\n".join(lines) + "\n"

    @staticmethod
    def _otel_tracked() -> bool:
        try:
            return ProjectTracking().is_installed(Section.FEATURES, "otel")
        except Exception:
            return False

    @staticmethod
    def _generate_openobserve_token(output_dir: Path) -> str:
        secret_path = output_dir / "app" / ".secrets" / "otel_openobserve_token"
        if secret_path.exists():
            return secret_path.read_text().strip()
        token = secrets.token_urlsafe(32)
        secret_path.parent.mkdir(parents=True, exist_ok=True)
        secret_path.write_text(token)
        print_console.info(f"  wrote  {secret_path}")
        return token

    def _write_observability(self, output_dir: Path) -> None:
        token = self._generate_openobserve_token(output_dir)
        collector_config = self._build_otel_collector_config(output_dir, token)
        self._write(
            output_dir / "app" / "otel-collector-config.yaml",
            collector_config,
        )
        openobserve_env = self._build_openobserve_env(token)
        self._write(
            output_dir / "app" / "openobserve.env",
            openobserve_env,
        )

    @staticmethod
    def _build_otel_collector_config(output_dir: Path, token: str) -> str:
        from ...features.otel.collector_config import build_collector_config

        # Derive project name from tracking or fallback
        try:
            tracking = ProjectTracking()
            project_name = tracking.get_config().get("project_name") or "your-app"
        except Exception:
            project_name = "your-app"
        return build_collector_config(
            project_name=project_name,
            otlp_endpoint="0.0.0.0:4318",
            openobserve_base_url="http://openobserve:5080",
            openobserve_authorization=f"Bearer {token}",
            stream_name=f"{project_name}-web",
        )

    @staticmethod
    def _build_openobserve_env(token: str) -> str:
        return f"""ZO_COLLECTOR_AUTH_TOKEN={token}
    """

    @staticmethod
    def _observability_services() -> dict:
        """Compose service definitions for otlp + openobserve (traefik-integrated)."""
        otlp: dict = {
            "image": "otel/opentelemetry-collector-contrib:0.159.0",
            "command": "--config=/etc/otelcol-contrib/config.yaml",
            "volumes": [
                "./otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml:ro"
            ],
            "env_file": ["openobserve.env"],
            "networks": ["traefik-public"],
            "restart": "unless-stopped",
        }
        openobserve: dict = {
            "image": "public.ecr.aws/zinclabs/openobserve:v0.92.2",
            "env_file": ["openobserve.env"],
            "environment": {
                "ZO_ROOT_USER_EMAIL": "admin@example.com",
                "ZO_ROOT_USER_PASSWORD": "ZoAdmin123!",
            },
            "volumes": ["openobserve-data:/data"],
            "networks": ["traefik-public"],
            "restart": "unless-stopped",
            "labels": [
                "traefik.enable=true",
                "traefik.http.routers.observe.rule=Host(`observe.$DOMAIN`)",
                "traefik.http.routers.observe.entrypoints=websecure",
                "traefik.http.routers.observe.tls.certresolver=letsencrypt",
                "traefik.http.services.observe.loadbalancer.server.port=5080",
                "traefik.docker.network=traefik-public",
            ],
        }
        return {"otlp": otlp, "openobserve": openobserve}

    @staticmethod
    def _build_base_compose(settings: CollectedSettings) -> str:
        secrets_block: dict = {}
        for secret in settings.secrets:
            secrets_block[secret.name] = {"file": str(Path(".secrets") / secret.name)}

        labels = [
            "traefik.enable=true",
            "traefik.http.routers.web.rule=Host(`$DOMAIN`)",
            "traefik.http.routers.web.entrypoints=websecure",
            "traefik.http.routers.web.tls.certresolver=letsencrypt",
            "traefik.http.services.web.loadbalancer.server.port=8000",
            "traefik.docker.network=traefik-public",
        ]

        service: dict = {
            "image": "${IMAGE:-your-app:latest}",
            "restart": "unless-stopped",
            "labels": labels,
            "env_file": [".env"],
            "healthcheck": {
                "test": [
                    "CMD",
                    "python",
                    "-c",
                    "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')",
                ],
                "interval": "30s",
                "timeout": "5s",
                "retries": 3,
            },
            "networks": ["traefik-public"],
        }
        if secrets_block:
            service["secrets"] = list(secrets_block.keys())

        compose: dict = {"services": {"web": service}}
        if secrets_block:
            compose["secrets"] = secrets_block
        compose["networks"] = {"traefik-public": {"external": True}}

        if DockerComposePlugin._otel_tracked():
            compose["services"].update(DockerComposePlugin._observability_services())
            compose["volumes"] = {"openobserve-data": None}

        lines = [
            "# Generated by ddx deploy docker-compose \u2014 do not edit this file.",
            "# Edit docker-compose.prod.yml to customise the deployment.",
            "",
        ]
        lines.append(
            yaml.dump(compose, default_flow_style=False, sort_keys=False).rstrip()
        )
        return "\n".join(lines) + "\n"


_OVERLAY_STUB = """\
# docker-compose.prod.yml \u2014 edit this file to customise your production deployment.
# This file extends docker-compose.base.yml. Re-running ddx deploy docker-compose
# will regenerate the base file but will never touch this file.
#
# Usage:
#   docker compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d

include:
  - docker-compose.base.yml

services:
  web:
    image: your-registry/your-app:latest
    # ports:
    #   - "8000:8000"
    # volumes:
    #   - ./staticfiles:/app/staticfiles
    # deploy:
    #   replicas: 2
    #   resources:
    #     limits:
    #       memory: 512M
"""

plugin = DockerComposePlugin()
app = plugin.typer_app
