import typer
import re

from typing import Annotated
from pathlib import Path

from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
)

from ..utils.print_console import print_success
from ..utils.color_conversion import generate_palette
from ..utils.file_content_change import remove_lines_from_file

app = typer.Typer(no_args_is_help=True)


def process_color(color: str) -> str:
    """Process color input - convert --color-* to var(--color-*) or return hex as is"""
    if color.startswith("--color-"):
        return f"var({color})"
    return color


def generate_color_palette(base_color: str) -> dict:
    """Generate color palette from base color if it's a hex color"""
    if base_color.startswith("#"):
        return generate_palette(base_color)
    raise ValueError("Color palettes can only be generated from hex color codes.")


def validate_color_input(color: str) -> str:
    """Validate color input format"""
    color = color.strip()

    # CSS variable format
    if color.startswith("--color-"):
        # Optional: validate CSS variable name format
        if not re.match(r"^--color-[a-zA-Z0-9-]+$", color):
            raise typer.BadParameter(
                "Invalid CSS variable format. Use format like --color-slate-700"
            )
        return color

    # Hex color format
    elif color.startswith("#"):
        # Validate hex color (3 or 6 digits)
        hex_part = color[1:]
        if not re.match(r"^[A-Fa-f0-9]{3}$|^[A-Fa-f0-9]{6}$", hex_part):
            raise typer.BadParameter(
                "Invalid hex color format. Use 3 or 6 digit hex codes like #FFF or #FFFFFF"
            )
        return color

    else:
        raise typer.BadParameter(
            "Invalid color format. Use hex color codes (e.g., #0047AB) or CSS variable format (e.g., --color-blue-500)."
        )


@app.command()
def install(
    primary_color: Annotated[
        str,
        typer.Option(
            help="Primary color (hex code or CSS variable). Example: #0047AB or --color-blue-500",
            prompt="Please enter the primary color",
            callback=validate_color_input,
        ),
    ] = "#0047AB",
    secondary_color: Annotated[
        str,
        typer.Option(
            help="Secondary color (hex code or CSS variable). Example: #2F739F or --color-slate-600",
            prompt="Please enter the secondary color",
            callback=validate_color_input,
        ),
    ] = "#2F739F",
    accent_color: Annotated[
        str,
        typer.Option(
            help="Accent color (hex code or CSS variable). Example: #F38B49 or --color-orange-500",
            prompt="Please enter the accent color",
            callback=validate_color_input,
        ),
    ] = "#F38B49",
    neutral_color: Annotated[
        str,
        typer.Option(
            help="Neutral color (hex code or CSS variable). Example: #728389 or --color-zinc-500",
            prompt="Please enter the neutral color",
            callback=validate_color_input,
        ),
    ] = "#728389",
    bg_light: Annotated[
        str,
        typer.Option(
            help="Background color for light theme (hex code or CSS variable). Example: #FFFFFF or --color-white",
            prompt="Please enter the background color for light theme",
            callback=validate_color_input,
        ),
    ] = "#FFFFFF",
    bg_secondary_light: Annotated[
        str,
        typer.Option(
            help="Secondary background color for light theme (hex code or CSS variable). Example: #84A8E0 or --color-primary-200",
            prompt="Please enter the secondary background color for light theme",
            callback=validate_color_input,
        ),
    ] = "--color-primary-200",
    bg_tertiary_light: Annotated[
        str,
        typer.Option(
            help="Tertiary background color for light theme (hex code or CSS variable). Example: #C8DFE9 or --color-secondary-200",
            prompt="Please enter the tertiary background color for light theme",
            callback=validate_color_input,
        ),
    ] = "--color-secondary-200",
    text_light: Annotated[
        str,
        typer.Option(
            help="Text color for light theme (hex code or CSS variable). Example: #0f172a or --color-slate-900",
            prompt="Please enter the text color for light theme",
            callback=validate_color_input,
        ),
    ] = "--color-slate-900",
    text_secondary_light: Annotated[
        str,
        typer.Option(
            help="Secondary text color for light theme (hex code or CSS variable). Example: #334155 or --color-slate-700",
            prompt="Please enter the secondary text color for light theme",
            callback=validate_color_input,
        ),
    ] = "--color-slate-700",
    text_muted_light: Annotated[
        str,
        typer.Option(
            help="Muted text color for light theme (hex code or CSS variable). Example: #64748b or --color-slate-500",
            prompt="Please enter the muted text color for light theme",
            callback=validate_color_input,
        ),
    ] = "--color-slate-500",
    bg_dark: Annotated[
        str,
        typer.Option(
            help="Background color for dark theme (hex code or CSS variable). Example: #0A0F1A",
            prompt="Please enter the background color for dark theme",
            callback=validate_color_input,
        ),
    ] = "#0A0F1A",
    bg_secondary_dark: Annotated[
        str,
        typer.Option(
            help="Secondary background color for dark theme (hex code or CSS variable). Example: #132035",
            prompt="Please enter the secondary background color for dark theme",
            callback=validate_color_input,
        ),
    ] = "#132035",
    bg_tertiary_dark: Annotated[
        str,
        typer.Option(
            help="Tertiary background color for dark theme (hex code or CSS variable). Example: #182945",
            prompt="Please enter the tertiary background color for dark theme",
            callback=validate_color_input,
        ),
    ] = "#182945",
    text_dark: Annotated[
        str,
        typer.Option(
            help="Text color for dark theme (hex code or CSS variable). Example: #f1f5f9 or --color-slate-100",
            prompt="Please enter the text color for dark theme",
            callback=validate_color_input,
        ),
    ] = "--color-slate-100",
    text_secondary_dark: Annotated[
        str,
        typer.Option(
            help="Secondary text color for dark theme (hex code or CSS variable). Example: #cbd5e1 or --color-slate-300",
            prompt="Please enter the secondary text color for dark theme",
            callback=validate_color_input,
        ),
    ] = "--color-slate-300",
    text_muted_dark: Annotated[
        str,
        typer.Option(
            help="Muted text color for dark theme (hex code or CSS variable). Example: #64748b or --color-slate-500",
            prompt="Please enter the muted text color for dark theme",
            callback=validate_color_input,
        ),
    ] = "--color-slate-500",
):
    """Install Tailwind theme with customizable colors."""

    is_project_exists_or_raise()

    primary_palette = generate_color_palette(primary_color)
    secondary_palette = generate_color_palette(secondary_color)
    accent_palette = generate_color_palette(accent_color)
    neutral_palette = generate_color_palette(neutral_color)

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "tailwind-theme"
    project_path = get_project_path()

    input_css_path = project_path / "tailwind" / "src" / "css" / "input.css"

    if not input_css_path.exists():
        typer.echo(
            "Tailwind CSS input file not found. Make sure Tailwind is set up correctly."
        )
        raise typer.Exit(code=1)

    template_context = {
        "primary_color": process_color(primary_color),
        "secondary_color": process_color(secondary_color),
        "accent_color": process_color(accent_color),
        "neutral_color": process_color(neutral_color),
        "bg_light": process_color(bg_light),
        "bg_secondary_light": process_color(bg_secondary_light),
        "bg_tertiary_light": process_color(bg_tertiary_light),
        "text_light": process_color(text_light),
        "text_secondary_light": process_color(text_secondary_light),
        "text_muted_light": process_color(text_muted_light),
        "bg_dark": process_color(bg_dark),
        "bg_secondary_dark": process_color(bg_secondary_dark),
        "bg_tertiary_dark": process_color(bg_tertiary_dark),
        "text_dark": process_color(text_dark),
        "text_secondary_dark": process_color(text_secondary_dark),
        "text_muted_dark": process_color(text_muted_dark),
        "primary_palette": primary_palette,
        "secondary_palette": secondary_palette,
        "accent_palette": accent_palette,
        "neutral_palette": neutral_palette,
    }

    copy_template_files(source_dir, project_path, template_context)

    input_content = input_css_path.read_text(encoding="utf-8")

    import_tailwind = '@import "tailwindcss";'
    import_theme = '@import "./theme.css";'

    if import_tailwind in input_content:
        replace_with = f"{import_tailwind}"
        if import_theme not in input_content:
            replace_with = f"{replace_with}\n{import_theme}"

        input_content = input_content.replace(import_tailwind, replace_with)

    input_css_path.write_text(input_content, encoding="utf-8")

    print_success("Tailwind theme installed successfully.")


@app.command()
def remove():
    """Remove Tailwind theme."""

    is_project_exists_or_raise()

    project_path = get_project_path()

    theme_css_path = project_path / "tailwind" / "src" / "css" / "theme.css"
    input_css_path = project_path / "tailwind" / "src" / "css" / "input.css"

    if theme_css_path.exists():
        theme_css_path.unlink()

    if input_css_path.exists():
        remove_lines_from_file(
            input_css_path,
            ['@import "./theme.css";'],
        )

    print_success("Tailwind theme removed successfully.")
