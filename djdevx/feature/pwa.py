import typer
import json

from typing import Annotated
from pathlib import Path
from PIL import Image

from ..utils.project_files import (
    copy_template_files,
    is_project_exists_or_raise,
    get_project_path,
)


app = typer.Typer(no_args_is_help=True)

manifest_json = {
    "name": "",
    "short_name": "",
    "description": "",
    "background_color": "",
    "theme_color": "",
    "start_url": "",
    "dir": "",
    "orientation": "",
    "display": "",
    "lang": "",
    "icons": [],
}


@app.command()
def pwa(
    name: Annotated[
        str,
        typer.Option(
            help="The display name for the application",
            prompt="Please enter the display name for the application",
        ),
    ],
    short_name: Annotated[
        str,
        typer.Option(
            help="The short name for the application when there is not enough space to display the name",
            prompt="Please enter the short name for the application",
        ),
    ],
    description: Annotated[
        str,
        typer.Option(
            help="The description of the application",
            prompt="Please enter the description of the application",
        ),
    ],
    icon_path: Annotated[
        Path,
        typer.Option(
            help="Path to the input icon file to be used for generating the PWA icons with different sizes",
            prompt="Please enter the path to the icon file to be used for generating the PWA icons",
        ),
    ] = Path("/tmp/icon.png"),
    background_color: Annotated[
        str,
        typer.Option(
            help="The page color of the window that the application will be opened in",
            prompt="Please enter the background color of the application",
        ),
    ] = "#ffffff",
    theme_color: Annotated[
        str,
        typer.Option(
            help="The theme color of the application",
            prompt="Please enter the theme color of the application",
        ),
    ] = "#000000",
    start_url: Annotated[
        str,
        typer.Option(
            help="The start URL of the application",
            prompt="Please enter the start URL of the application",
        ),
    ] = "/",
    dir: Annotated[
        str,
        typer.Option(
            help="The base direction of the application",
            prompt="Please enter the base direction of the application",
        ),
    ] = "ltr",
    scope: Annotated[
        str,
        typer.Option(
            help="Defines which URL are within the navigation scope of your application. Scope can often just be set to the base URL of your PWA.",
            prompt="Please enter the scope of the application",
        ),
    ] = "",
    orientation: Annotated[
        str,
        typer.Option(
            help="The default orientation of the application. Options are [any, natural, landscape, landscape-primary, landscape-secondary, portrait, portrait-primary, portrait-secondary]",
            prompt="Please enter the default orientation of the application",
        ),
    ] = "portrait",
    display: Annotated[
        str,
        typer.Option(
            help="The display mode that the website should default to. Options are [fullscreen, standalone, minimal-ui, browser]",
            prompt="Please enter the display mode of the application",
        ),
    ] = "standalone",
    language: Annotated[
        str,
        typer.Option(
            help="The primary language of the application",
            prompt="Please enter the primary language of the application",
        ),
    ] = "en",
):
    """
    Add PWA support to the project
    """
    is_project_exists_or_raise()

    current_dir = Path(__file__).resolve().parent
    source_dir = current_dir.parent / "templates" / "pwa"
    project_dir = get_project_path()

    copy_template_files(
        source_dir=source_dir,
        dest_dir=project_dir,
        template_context={},
    )

    manifest_json["name"] = name
    manifest_json["short_name"] = short_name
    manifest_json["description"] = description
    manifest_json["background_color"] = background_color
    manifest_json["theme_color"] = theme_color
    manifest_json["start_url"] = start_url
    manifest_json["dir"] = dir
    manifest_json["orientation"] = orientation
    manifest_json["display"] = display
    manifest_json["lang"] = language
    if scope:
        manifest_json["scope"] = scope

    resize_android_icon(icon_path, project_dir)
    resize_ios_icon(icon_path, project_dir)
    resize_windows11_icon(icon_path, project_dir)
    generate_ios_splash_screens(icon_path, project_dir)
    write_manifest_json(project_dir)
    update_base_html(project_dir)


def resize_android_icon(icon_path, project_dir):
    android_icon_sizes = [48, 72, 96, 144, 192, 512]
    base_icon = Image.open(icon_path)

    for size in android_icon_sizes:
        resized_icon = base_icon.resize((size, size), Image.Resampling.LANCZOS)
        icon_filename = f"android-launchericon-{size}x{size}.png"
        icons_dir = project_dir / "static" / "images" / "icons" / "android"
        Path(icons_dir).mkdir(parents=True, exist_ok=True)
        icon_file = icons_dir / icon_filename
        resized_icon.save(icon_file)

        manifest_json["icons"].append(
            {
                "src": "{% static '" + f"images/icons/android/{icon_filename}" + "' %}",
                "sizes": f"{size}x{size}",
                "type": "image/png",
            }
        )

        if size == 512:
            manifest_json["icons"].append(
                {
                    "src": "{% static '"
                    + f"images/icons/android/{icon_filename}"
                    + "' %}",
                    "sizes": f"{size}x{size}",
                    "type": "image/png",
                    "purpose": "maskable",
                }
            )


def resize_ios_icon(icon_path, project_dir):
    ios_icon_sizes = [
        16,
        20,
        29,
        32,
        40,
        50,
        57,
        58,
        60,
        64,
        72,
        76,
        80,
        87,
        100,
        114,
        120,
        128,
        144,
        152,
        167,
        180,
        192,
        256,
        512,
        1024,
    ]

    base_icon = Image.open(icon_path)

    for size in ios_icon_sizes:
        resized_icon = base_icon.resize((size, size), Image.Resampling.LANCZOS)
        icon_dir = project_dir / "static" / "images" / "icons" / "ios"
        Path(icon_dir).mkdir(parents=True, exist_ok=True)
        resized_icon.save(icon_dir / f"{size}.png")

        manifest_json["icons"].append(
            {
                "src": "{% static '" + f"images/icons/ios/{size}.png" + "' %}",
                "sizes": f"{size}x{size}",
                "type": "image/png",
            }
        )

        if size == 512:
            manifest_json["icons"].append(
                {
                    "src": "{% static '" + f"images/icons/ios/{size}.png" + "' %}",
                    "sizes": f"{size}x{size}",
                    "type": "image/png",
                    "purpose": "maskable",
                }
            )


def resize_windows11_icon(icon_path, project_dir):
    windows11_configs = {
        "SmallTile": [
            (71, 71, 100),
            (89, 89, 125),
            (107, 107, 150),
            (142, 142, 200),
            (284, 284, 400),
        ],
        "Square150x150Logo": [
            (150, 150, 100),
            (188, 188, 125),
            (225, 225, 150),
            (300, 300, 200),
            (600, 600, 400),
        ],
        "Wide310x150Logo": [
            (310, 150, 100),
            (388, 188, 125),
            (465, 225, 150),
            (620, 300, 200),
            (1240, 600, 400),
        ],
        "LargeTile": [
            (310, 310, 100),
            (388, 388, 125),
            (465, 465, 150),
            (620, 620, 200),
            (1240, 1240, 400),
        ],
        "Square44x44Logo": [
            (44, 44, 100),
            (55, 55, 125),
            (66, 66, 150),
            (88, 88, 200),
            (176, 176, 400),
        ],
        "StoreLogo": [
            (50, 50, 100),
            (63, 63, 125),
            (75, 75, 150),
            (100, 100, 200),
            (200, 200, 400),
        ],
        "SplashScreen": [
            (620, 300, 100),
            (775, 375, 125),
            (930, 450, 150),
            (1240, 600, 200),
            (2480, 1200, 400),
        ],
    }

    target_sizes = [16, 20, 24, 30, 32, 36, 40, 44, 48, 60, 64, 72, 80, 96, 256]

    base_icon = Image.open(icon_path)
    icons_dir = project_dir / "static" / "images" / "icons" / "windows11"
    Path(icons_dir).mkdir(parents=True, exist_ok=True)

    manifest_icons = []

    for logo_type, sizes in windows11_configs.items():
        for width, height, scale in sizes:
            icon_filename = f"{logo_type}.scale-{scale}.png"
            resized_icon = base_icon.resize((width, height), Image.Resampling.LANCZOS)
            icon_file = icons_dir / icon_filename
            resized_icon.save(icon_file)

            manifest_icons.append(
                {
                    "src": "{% static 'images/icons/windows11/"
                    + icon_filename
                    + "' %}",
                    "sizes": f"{width}x{height}",
                    "type": "image/png",
                }
            )

    for size in target_sizes:
        icon_filename = f"Square44x44Logo.targetsize-{size}.png"
        resized_icon = base_icon.resize((size, size), Image.Resampling.LANCZOS)
        icon_file = icons_dir / icon_filename
        resized_icon.save(icon_file)
        manifest_icons.append(
            {
                "src": "{% static 'images/icons/windows11/" + icon_filename + "' %}",
                "sizes": f"{size}x{size}",
                "type": "image/png",
            }
        )

        icon_filename = f"Square44x44Logo.altform-unplated_targetsize-{size}.png"
        icon_file = icons_dir / icon_filename
        resized_icon.save(icon_file)
        manifest_icons.append(
            {
                "src": "{% static 'images/icons/windows11/" + icon_filename + "' %}",
                "sizes": f"{size}x{size}",
                "type": "image/png",
            }
        )

        icon_filename = f"Square44x44Logo.altform-lightunplated_targetsize-{size}.png"
        icon_file = icons_dir / icon_filename
        resized_icon.save(icon_file)
        manifest_icons.append(
            {
                "src": "{% static 'images/icons/windows11/" + icon_filename + "' %}",
                "sizes": f"{size}x{size}",
                "type": "image/png",
            }
        )

    manifest_json["icons"].extend(manifest_icons)


def generate_ios_splash_screens(icon_path, project_dir):
    splash_screens = {
        "iPhone_15_Pro_Max__iPhone_15_Plus__iPhone_14_Pro_Max": {
            "portrait": (
                1290,
                2796,
                "(device-width: 430px) and (device-height: 932px) and (-webkit-device-pixel-ratio: 3)",
            ),
            "landscape": (
                2796,
                1290,
                "(device-width: 430px) and (device-height: 932px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
            ),
        },
        "iPhone_15_Pro__iPhone_15__iPhone_14_Pro": {
            "portrait": (
                1179,
                2556,
                "(device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3)",
            ),
            "landscape": (
                2556,
                1179,
                "(device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
            ),
        },
        "iPhone_14_Plus__iPhone_13_Pro_Max__iPhone_12_Pro_Max": {
            "portrait": (
                1284,
                2778,
                "(device-width: 428px) and (device-height: 926px) and (-webkit-device-pixel-ratio: 3)",
            ),
            "landscape": (
                2778,
                1284,
                "(device-width: 428px) and (device-height: 926px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
            ),
        },
        "iPhone_14__iPhone_13_Pro__iPhone_13__iPhone_12_Pro__iPhone_12": {
            "portrait": (
                1170,
                2532,
                "(device-width: 390px) and (device-height: 844px) and (-webkit-device-pixel-ratio: 3)",
            ),
            "landscape": (
                2532,
                1170,
                "(device-width: 390px) and (device-height: 844px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
            ),
        },
        "iPhone_13_mini__iPhone_12_mini__iPhone_11_Pro__iPhone_XS__iPhone_X": {
            "portrait": (
                1125,
                2436,
                "(device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3)",
            ),
            "landscape": (
                2436,
                1125,
                "(device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
            ),
        },
        "iPhone_11_Pro_Max__iPhone_XS_Max": {
            "portrait": (
                1242,
                2688,
                "(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 3)",
            ),
            "landscape": (
                2688,
                1242,
                "(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
            ),
        },
        "iPhone_11__iPhone_XR": {
            "portrait": (
                828,
                1792,
                "(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                1792,
                828,
                "(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
        "iPhone_8_Plus__iPhone_7_Plus__iPhone_6s_Plus__iPhone_6_Plus": {
            "portrait": (
                1242,
                2208,
                "(device-width: 414px) and (device-height: 736px) and (-webkit-device-pixel-ratio: 3)",
            ),
            "landscape": (
                2208,
                1242,
                "(device-width: 414px) and (device-height: 736px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
            ),
        },
        "iPhone_8__iPhone_7__iPhone_6s__iPhone_6__4.7__iPhone_SE": {
            "portrait": (
                750,
                1334,
                "(device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                1334,
                750,
                "(device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
        "4__iPhone_SE__iPod_touch_5th_generation_and_later": {
            "portrait": (
                640,
                1136,
                "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                1136,
                640,
                "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
        "12.9__iPad_Pro": {
            "landscape": (
                2732,
                2048,
                "(device-width: 1024px) and (device-height: 1366px) and (-webkit-device-pixel-ratio: 2)",
            )
        },
        "11__iPad_Pro__10.5__iPad_Pro": {
            "portrait": (
                1668,
                2388,
                "(device-width: 834px) and (device-height: 1194px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                2388,
                1668,
                "(device-width: 834px) and (device-height: 1194px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
        "10.9__iPad_Air": {
            "portrait": (
                1640,
                2360,
                "(device-width: 820px) and (device-height: 1180px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                2360,
                1640,
                "(device-width: 820px) and (device-height: 1180px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
        "10.5__iPad_Air": {
            "portrait": (
                1668,
                2224,
                "(device-width: 834px) and (device-height: 1112px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                2224,
                1668,
                "(device-width: 834px) and (device-height: 1112px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
        "10.2__iPad": {
            "portrait": (
                1620,
                2160,
                "(device-width: 810px) and (device-height: 1080px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                2160,
                1620,
                "(device-width: 810px) and (device-height: 1080px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
        "8.3__iPad_Mini": {
            "portrait": (
                1488,
                2266,
                "(device-width: 744px) and (device-height: 1133px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                2266,
                1488,
                "(device-width: 744px) and (device-height: 1133px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
        "9.7__iPad_Pro__7.9__iPad_mini__9.7__iPad_Air__9.7__iPad": {
            "portrait": (
                1536,
                2048,
                "(device-width: 768px) and (device-height: 1024px) and (-webkit-device-pixel-ratio: 2)",
            ),
            "landscape": (
                2048,
                1536,
                "(device-width: 768px) and (device-height: 1024px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
            ),
        },
    }

    splash_screens_dir = project_dir / "static" / "images" / "icons" / "splash_screens"
    Path(splash_screens_dir).mkdir(parents=True, exist_ok=True)

    icon_image = Image.open(icon_path)
    icon_image.save(splash_screens_dir / "icon.png")

    splash_screen_content = ["{% load static %}"]

    for device_name, orientations in splash_screens.items():
        for orientation, (width, height, media) in orientations.items():
            filename = f"{device_name}_{orientation}.png"
            splash = Image.new("RGB", (width, height), "white")
            icon_size = min(width, height) // 4
            icon_resized = icon_image.resize(
                (icon_size, icon_size), Image.Resampling.LANCZOS
            )
            icon_x = (width - icon_size) // 2
            icon_y = (height - icon_size) // 2
            if icon_resized.mode == "RGBA":
                splash.paste(icon_resized, (icon_x, icon_y), icon_resized)
            else:
                splash.paste(icon_resized, (icon_x, icon_y))

            output_path = splash_screens_dir / filename
            splash.save(output_path, quality=95, optimize=True)

            splash_screen_content.append(
                '<link rel="apple-touch-startup-image" media="'
                + f"{media}"
                + '" href="{% static '
                + f"'images/icons/splash_screens/{filename}'"
                + ' %}">'
            )

    with open(project_dir / "templates" / "apple_splash.html", "w") as f:
        f.write("\n".join(splash_screen_content))


def write_manifest_json(project_dir):
    manifest_text = json.dumps(manifest_json, indent=4)

    content = "{% load static %} \n" + f"{manifest_text}"

    directory = project_dir / "pwa" / "templates"
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(directory / "manifest.json", "w") as f:
        f.write(content)


def update_base_html(project_dir):
    base_html_path = project_dir / "templates" / "_base.html"
    with open(base_html_path, "r") as f:
        content = f.read()

    content = content.replace(
        "</head>",
        '  <link rel="manifest" href="/manifest.json"> \n    {% include "apple_splash.html" %}\n  </head>',
    )

    with open(base_html_path, "w") as f:
        f.write(content)
