"""BaseFramework — thin wrapper over InstallableBase for the frameworks domain."""

import re
import urllib.request
from pathlib import Path

from ..utils.installable.installable import Installable


class BaseFramework(Installable):
    """Base class for CSS/JS frameworks."""

    section: str = "frameworks"

    css_url: str = ""
    css_filename: str = ""
    js_url: str = ""
    js_filename: str = ""
    js_module: bool = False

    @classmethod
    def get_registry(cls):
        from ._registry import FRAMEWORK_REGISTRY

        return FRAMEWORK_REGISTRY

    @property
    def _base_template_path(self) -> Path:
        return self.structure.base_template

    @property
    def _style_tag(self) -> str:
        return f'<link rel="stylesheet" href="{{\% static \'css/{self.css_filename}\' %}}">'

    @property
    def _script_tag(self) -> str:
        tm = ' type="module"' if self.js_module else ""
        return f"<script{tm} src=\"{{% static 'js/{self.js_filename}' %}}\"></script>"

    def _download(self, url: str, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception:
            dest.write_text("/* placeholder */\n")

    def after_copy_templates(self) -> None:
        self._install_framework()

    def before_pixi_remove(self) -> None:
        super().before_pixi_remove()
        self._uninstall_framework()

    def _install_framework(self) -> None:
        if self.css_url and self.css_filename:
            dest = self.structure.static_css_dir / self.css_filename
            if not dest.exists():
                self._download(self.css_url, dest)

        if self.js_url and self.js_filename:
            dest = self.structure.static_js_dir / self.js_filename
            if not dest.exists():
                self._download(self.js_url, dest)

        self._modify_base_template(install=True)

    def _uninstall_framework(self) -> None:
        self._modify_base_template(install=False)

        if self.css_filename:
            (self.structure.static_css_dir / self.css_filename).unlink(missing_ok=True)
        if self.js_filename:
            (self.structure.static_js_dir / self.js_filename).unlink(missing_ok=True)

    def _modify_base_template(self, install: bool = True) -> None:
        path = self._base_template_path
        if not path.exists():
            return
        content = path.read_text()

        if install:
            if self.css_filename and self.css_filename not in content:
                content = content.replace(
                    "</head>", f"    {self._style_tag}\n  </head>"
                )
            if self.js_filename and self.js_filename not in content:
                content = content.replace(
                    "</body>", f"    {self._script_tag}\n  </body>"
                )
        else:
            if self.css_filename:
                content = re.sub(
                    r"\s*" + re.escape(self._style_tag) + r"\s*\n?",
                    "",
                    content,
                )
            if self.js_filename:
                content = re.sub(
                    r"\s*" + re.escape(self._script_tag) + r"\s*\n?",
                    "",
                    content,
                )

        path.write_text(content)
