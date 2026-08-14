from pathlib import Path
import re

from .._base import BaseFramework
from .._registry import register


@register
class StartingPointUIFramework(BaseFramework):
    name: str = "starting_point_ui"
    display_name: str = "Starting Point UI"
    description: str = "Starting Point UI CSS/JS framework"

    @property
    def _css_path(self) -> Path:
        return self.structure.root / "tailwind" / "src" / "css" / "starting-point.css"

    @property
    def _js_path(self) -> Path:
        return self.structure.static_js_dir / "vendor" / "starting-point.js"

    @property
    def _input_css_path(self) -> Path:
        return self.structure.tailwind_input_css

    def after_copy_templates(self) -> None:
        self._css_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._css_path.exists():
            self._css_path.write_text("/* starting-point placeholder */\n")

        self._js_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._js_path.exists():
            self._js_path.write_text("/* starting-point js placeholder */\n")

        input_existed = self._input_css_path.exists()
        if not input_existed:
            self._input_css_path.parent.mkdir(parents=True, exist_ok=True)
            self._input_css_path.write_text("/* input.css */\n")
        content = self._input_css_path.read_text()
        if '@import "./starting-point.css";' not in content:
            content = '@import "./starting-point.css";\n' + content
            self._input_css_path.write_text(content)

        path = self._base_template_path
        if path.exists():
            template = path.read_text()
            if "starting-point.js" not in template:
                tag = "<script src=\"{% static 'js/vendor/starting-point.js' %}\"></script>"
                template = template.replace("</body>", f"    {tag}\n  </body>")
                path.write_text(template)

    def before_pixi_remove(self) -> None:
        self._css_path.unlink(missing_ok=True)
        self._js_path.unlink(missing_ok=True)

        if self._input_css_path.exists():
            content = self._input_css_path.read_text()
            content = content.replace('@import "./starting-point.css";\n', "")
            self._input_css_path.write_text(content)

        path = self._base_template_path
        if path.exists():
            template = path.read_text()
            tag = "<script src=\"{% static 'js/vendor/starting-point.js' %}\"></script>"
            template = re.sub(r"\s*" + re.escape(tag) + r"\s*\n?", "", template)
            path.write_text(template)
