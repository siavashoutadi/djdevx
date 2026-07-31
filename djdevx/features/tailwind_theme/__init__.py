from .._base import BaseFeature
from .._registry import register
from ...utils.installable.types import InstallParam
from ...utils.color.converter import color_converter


@register
class TailwindThemeFeature(BaseFeature):
    name: str = "tailwind_theme"
    display_name: str = "Tailwind Theme"
    description: str = "Tailwind CSS theme with color palette"

    install_params: list[InstallParam] = [
        InstallParam(
            name="primary_color",
            prompt="Please enter the primary color",
            default="#0047AB",
        ),
        InstallParam(
            name="secondary_color",
            prompt="Please enter the secondary color",
            default="#2F739F",
        ),
        InstallParam(
            name="accent_color",
            prompt="Please enter the accent color",
            default="#F38B49",
        ),
        InstallParam(
            name="neutral_color",
            prompt="Please enter the neutral color",
            default="#728389",
        ),
        InstallParam(
            name="bg_light",
            prompt="Please enter the background color for light theme",
            default="#FFFFFF",
        ),
        InstallParam(
            name="bg_secondary_light",
            prompt="Please enter the secondary background color for light theme",
            default="#FBFBFB",
        ),
        InstallParam(
            name="bg_tertiary_light",
            prompt="Please enter the tertiary background color for light theme",
            default="#F8FFFF",
        ),
        InstallParam(
            name="text_light",
            prompt="Please enter the text color for light theme",
            default="--color-slate-900",
        ),
        InstallParam(
            name="text_secondary_light",
            prompt="Please enter the secondary text color for light theme",
            default="--color-slate-700",
        ),
        InstallParam(
            name="text_muted_light",
            prompt="Please enter the muted text color for light theme",
            default="--color-slate-500",
        ),
        InstallParam(
            name="bg_dark",
            prompt="Please enter the background color for dark theme",
            default="#0A0F1A",
        ),
        InstallParam(
            name="bg_secondary_dark",
            prompt="Please enter the secondary background color for dark theme",
            default="#132035",
        ),
        InstallParam(
            name="bg_tertiary_dark",
            prompt="Please enter the tertiary background color for dark theme",
            default="#182945",
        ),
        InstallParam(
            name="text_dark",
            prompt="Please enter the text color for dark theme",
            default="--color-slate-100",
        ),
        InstallParam(
            name="text_secondary_dark",
            prompt="Please enter the secondary text color for dark theme",
            default="--color-slate-300",
        ),
        InstallParam(
            name="text_muted_dark",
            prompt="Please enter the muted text color for dark theme",
            default="--color-slate-500",
        ),
    ]

    @staticmethod
    def _process_color(color: str) -> str:
        if color.startswith("--color-"):
            return f"var({color})"
        return color

    def _enrich_context(self) -> None:
        ctx = self._install_context

        palette_map = {
            "primary_color": "primary_palette",
            "secondary_color": "secondary_palette",
            "accent_color": "accent_palette",
            "neutral_color": "neutral_palette",
        }
        for color_key, palette_key in palette_map.items():
            hex_val = ctx.get(color_key, "")
            ctx[palette_key] = color_converter.generate_palette(hex_val)
            ctx[color_key] = self._process_color(hex_val)

        non_palette_keys = [
            "bg_light",
            "bg_secondary_light",
            "bg_tertiary_light",
            "text_light",
            "text_secondary_light",
            "text_muted_light",
            "bg_dark",
            "bg_secondary_dark",
            "bg_tertiary_dark",
            "text_dark",
            "text_secondary_dark",
            "text_muted_dark",
        ]
        for key in non_palette_keys:
            ctx[key] = self._process_color(ctx.get(key, ""))

    def before_copy_templates(self) -> None:
        self._enrich_context()

    def after_copy_templates(self) -> None:
        input_css = self.structure.tailwind_input_css
        if input_css.exists():
            content = input_css.read_text()
            if '@import "./theme.css";' not in content:
                content = '@import "./theme.css";\n' + content
                input_css.write_text(content)

    def before_pixi_remove(self) -> None:
        input_css = self.structure.tailwind_input_css
        if input_css.exists():
            content = input_css.read_text()
            content = content.replace('@import "./theme.css";\n', "")
            input_css.write_text(content)
