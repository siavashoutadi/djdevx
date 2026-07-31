from ...utils.installable.types import InstallableRef, PACKAGE

from .._base import BaseFeature
from .._registry import register


@register
class TailwindUIFeature(BaseFeature):
    name: str = "tailwind_ui"
    display_name: str = "Tailwind UI"
    description: str = "Tailwind UI components (alerts, badges, buttons, toasts, cards)"
    needs: list[InstallableRef] = [InstallableRef("django-tailwind-cli", PACKAGE)]

    def after_copy_templates(self) -> None:
        input_css = self.structure.tailwind_input_css
        if input_css.exists():
            content = input_css.read_text()
            if '@import "./tailwind-ui/all.css";' not in content:
                content = content.replace(
                    '@import "tailwindcss";',
                    '@import "./tailwind-ui/all.css";\n@import "tailwindcss";',
                )
                input_css.write_text(content)

    def before_pixi_remove(self) -> None:
        super().before_pixi_remove()
        input_css = self.structure.tailwind_input_css
        if input_css.exists():
            content = input_css.read_text()
            content = content.replace('@import "./tailwind-ui/all.css";\n', "")
            input_css.write_text(content)
