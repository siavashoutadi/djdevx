import shutil

from ....utils.templates.manager import TemplateManager
from ._base import BasePackage


class ChannelsPackage(BasePackage):
    name = "channels"
    packages = ["channels>=4.3.2,<5", "daphne>=4.2.3,<5", "channels_redis>=4.3.0,<5"]
    dev_packages = [
        "twisted>=26.4.0,<27",
        "h2>=4.3.0,<5",
        "priority>=1.3.0,<2",
        "pyopenssl>=26.3.0,<27",
        "service_identity>=26.1.0,<27",
        "idna>=3.18,<4",
    ]

    def after_pixi_remove(self) -> None:
        """Remove ws_urls directory and restore original ASGI file."""
        shutil.rmtree(self.pm.ws_urls_path, ignore_errors=True)

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
