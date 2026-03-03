import shutil

from ....utils.templates.manager import TemplateManager
from ._base import BasePackage


class ChannelsPackage(BasePackage):
    name = "channels"
    packages = ["channels[daphne]", "channels_redis"]
    dev_packages = ["twisted[http2,tls]"]
    env_vars = {
        "CHANNEL_LAYERS_REDIS_HOST": "redis://default:${REDIS_PASSWORD}@cache:6379/1",
    }

    def remove(self) -> None:
        """Remove channels and restore original ASGI file."""
        super().remove()

        # Remove the entire ws_urls directory
        ws_url_path = self.pm.ws_urls_path
        shutil.rmtree(ws_url_path, ignore_errors=True)

        # Restore original ASGI file without channels
        template_asgi_path = (
            self.djdevx_root
            / "templates"
            / "new"
            / "backend"
            / "django"
            / "{{backend_root}}"
            / "applications"
            / "asgi.py"
        )

        template_manager = TemplateManager()
        template_manager.copy_template(
            source_file=template_asgi_path,
            dest_dir=self.pm.project_path / "applications",
            template_context={"backend_root": "backend"},
        )


_pkg = ChannelsPackage(__file__)
app = _pkg.app
