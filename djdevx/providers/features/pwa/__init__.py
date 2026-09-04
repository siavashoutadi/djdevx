import json
from pathlib import Path

from PIL import Image

from .._base import BaseFeature
from .._registry import register
from ....utils.console.print import print_console
from ....installable.models import InstallParam


@register
class PWAFeature(BaseFeature):
    name: str = "pwa"
    display_name: str = "PWA"
    description: str = "Progressive Web App support with service worker and manifest"

    install_params: list[InstallParam] = [
        InstallParam(
            name="app_name",
            prompt="Please enter the display name for the application",
        ),
        InstallParam(
            name="short_name",
            prompt="Please enter the short name for the application",
        ),
        InstallParam(
            name="description",
            prompt="Please enter the description of the application",
        ),
        InstallParam(
            name="icon_path",
            prompt="Path to the icon file to be used for generating the PWA icons",
            default="static/images/logo.svg",
        ),
        InstallParam(
            name="background_color",
            prompt="Please enter the background color of the application",
            default="#ffffff",
        ),
        InstallParam(
            name="theme_color",
            prompt="Please enter the theme color of the application",
            default="#000000",
        ),
        InstallParam(
            name="start_url",
            prompt="Please enter the start URL of the application",
            default="/",
        ),
        InstallParam(
            name="dir",
            prompt="Please enter the base direction of the application",
            default="ltr",
        ),
        InstallParam(
            name="scope",
            prompt="Please enter the scope of the application (leave empty to skip)",
            default="",
        ),
        InstallParam(
            name="orientation",
            prompt="Please enter the default orientation of the application",
            default="portrait",
        ),
        InstallParam(
            name="display",
            prompt="Please enter the display mode of the application",
            default="standalone",
        ),
        InstallParam(
            name="language",
            prompt="Please enter the primary language of the application",
            default="en",
        ),
    ]

    files_to_remove: list[str] = [
        "pwa/templates/manifest.json",
        "templates/apple_splash.html",
    ]
    folders_to_remove: list[str] = [
        "static/images/icons/android",
        "static/images/icons/ios",
        "static/images/icons/windows11",
        "static/images/icons/splash_screens",
    ]

    def after_copy_templates(self, step=None) -> None:
        self._manifest_icons: list[dict] = []
        self._generate_icons()
        self._write_manifest()
        self._update_base_html()

    def before_pixi_remove(self, step=None) -> None:
        self._remove_from_base_html()

    # ------------------------------------------------------------------
    # Icon generation
    # ------------------------------------------------------------------

    def _resolve_icon_path(self) -> Path | None:
        icon_path = self._install_context.get("icon_path", "")
        if not icon_path:
            return None
        path = Path(icon_path)
        if not path.is_absolute():
            path = self.structure.root / path
        return path if path.exists() else None

    def _generate_icons(self) -> None:
        icon_path = self._resolve_icon_path()
        if icon_path is None:
            return
        try:
            base_icon = Image.open(icon_path)
            base_icon.verify()
            base_icon = Image.open(icon_path)
        except (OSError, ValueError) as exc:
            print_console.info(
                f"Could not read icon {icon_path} ({exc}); skipping generated icons."
            )
            return
        self._resize_android_icons(base_icon.copy())
        self._resize_ios_icons(base_icon.copy())
        self._resize_windows11_icons(base_icon.copy())
        self._generate_splash_screens(base_icon.copy())

    def _resize_android_icons(self, base_icon: Image.Image) -> None:
        sizes = [48, 72, 96, 144, 192, 512]
        icons_dir = self.structure.root / "static" / "images" / "icons" / "android"
        icons_dir.mkdir(parents=True, exist_ok=True)

        for size in sizes:
            resized = base_icon.resize((size, size), Image.Resampling.LANCZOS)
            filename = f"android-launchericon-{size}x{size}.png"
            resized.save(icons_dir / filename)
            self._manifest_icons.append(
                {
                    "src": "{%% static 'images/icons/android/%s' %%}" % filename,
                    "sizes": f"{size}x{size}",
                    "type": "image/png",
                }
            )
            if size == 512:
                self._manifest_icons.append(
                    {
                        "src": "{%% static 'images/icons/android/%s' %%}" % filename,
                        "sizes": f"{size}x{size}",
                        "type": "image/png",
                        "purpose": "maskable",
                    }
                )

    def _resize_ios_icons(self, base_icon: Image.Image) -> None:
        sizes = [
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
        icons_dir = self.structure.root / "static" / "images" / "icons" / "ios"
        icons_dir.mkdir(parents=True, exist_ok=True)

        for size in sizes:
            resized = base_icon.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(icons_dir / f"{size}.png")
            self._manifest_icons.append(
                {
                    "src": "{%% static 'images/icons/ios/%s.png' %%}" % size,
                    "sizes": f"{size}x{size}",
                    "type": "image/png",
                }
            )
            if size == 512:
                self._manifest_icons.append(
                    {
                        "src": "{%% static 'images/icons/ios/%s.png' %%}" % size,
                        "sizes": f"{size}x{size}",
                        "type": "image/png",
                        "purpose": "maskable",
                    }
                )

    def _resize_windows11_icons(self, base_icon: Image.Image) -> None:
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

        icons_dir = self.structure.root / "static" / "images" / "icons" / "windows11"
        icons_dir.mkdir(parents=True, exist_ok=True)

        for logo_type, sizes in windows11_configs.items():
            for width, height, scale in sizes:
                filename = f"{logo_type}.scale-{scale}.png"
                resized = base_icon.resize((width, height), Image.Resampling.LANCZOS)
                resized.save(icons_dir / filename)
                self._manifest_icons.append(
                    {
                        "src": "{%% static 'images/icons/windows11/%s' %%}" % filename,
                        "sizes": f"{width}x{height}",
                        "type": "image/png",
                    }
                )

        for size in target_sizes:
            variants = [
                f"Square44x44Logo.targetsize-{size}.png",
                f"Square44x44Logo.altform-unplated_targetsize-{size}.png",
                f"Square44x44Logo.altform-lightunplated_targetsize-{size}.png",
            ]
            for filename in variants:
                resized = base_icon.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(icons_dir / filename)
                self._manifest_icons.append(
                    {
                        "src": "{%% static 'images/icons/windows11/%s' %%}" % filename,
                        "sizes": f"{size}x{size}",
                        "type": "image/png",
                    }
                )

    # ------------------------------------------------------------------
    # Splash screens
    # ------------------------------------------------------------------

    def _generate_splash_screens(self, base_icon: Image.Image) -> None:
        splash_configs = {
            "iPhone_15_Pro_Max__iPhone_15_Plus__iPhone_14_Pro_Max": [
                (
                    1290,
                    2796,
                    "(device-width: 430px) and (device-height: 932px) and (-webkit-device-pixel-ratio: 3)",
                    "portrait",
                ),
                (
                    2796,
                    1290,
                    "(device-width: 430px) and (device-height: 932px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "iPhone_15_Pro__iPhone_15__iPhone_14_Pro": [
                (
                    1179,
                    2556,
                    "(device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3)",
                    "portrait",
                ),
                (
                    2556,
                    1179,
                    "(device-width: 393px) and (device-height: 852px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "iPhone_14_Plus__iPhone_13_Pro_Max__iPhone_12_Pro_Max": [
                (
                    1284,
                    2778,
                    "(device-width: 428px) and (device-height: 926px) and (-webkit-device-pixel-ratio: 3)",
                    "portrait",
                ),
                (
                    2778,
                    1284,
                    "(device-width: 428px) and (device-height: 926px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "iPhone_14__iPhone_13_Pro__iPhone_13__iPhone_12_Pro__iPhone_12": [
                (
                    1170,
                    2532,
                    "(device-width: 390px) and (device-height: 844px) and (-webkit-device-pixel-ratio: 3)",
                    "portrait",
                ),
                (
                    2532,
                    1170,
                    "(device-width: 390px) and (device-height: 844px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "iPhone_13_mini__iPhone_12_mini__iPhone_11_Pro__iPhone_XS__iPhone_X": [
                (
                    1125,
                    2436,
                    "(device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3)",
                    "portrait",
                ),
                (
                    2436,
                    1125,
                    "(device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "iPhone_11_Pro_Max__iPhone_XS_Max": [
                (
                    1242,
                    2688,
                    "(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 3)",
                    "portrait",
                ),
                (
                    2688,
                    1242,
                    "(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "iPhone_11__iPhone_XR": [
                (
                    828,
                    1792,
                    "(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    1792,
                    828,
                    "(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "iPhone_8_Plus__iPhone_7_Plus__iPhone_6s_Plus__iPhone_6_Plus": [
                (
                    1242,
                    2208,
                    "(device-width: 414px) and (device-height: 736px) and (-webkit-device-pixel-ratio: 3)",
                    "portrait",
                ),
                (
                    2208,
                    1242,
                    "(device-width: 414px) and (device-height: 736px) and (-webkit-device-pixel-ratio: 3) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "iPhone_8__iPhone_7__iPhone_6s__iPhone_6__4.7__iPhone_SE": [
                (
                    750,
                    1334,
                    "(device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    1334,
                    750,
                    "(device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "4__iPhone_SE__iPod_touch_5th_generation_and_later": [
                (
                    640,
                    1136,
                    "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    1136,
                    640,
                    "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "12.9__iPad_Pro": [
                (
                    2732,
                    2048,
                    "(device-width: 1024px) and (device-height: 1366px) and (-webkit-device-pixel-ratio: 2)",
                    "landscape",
                ),
            ],
            "11__iPad_Pro__10.5__iPad_Pro": [
                (
                    1668,
                    2388,
                    "(device-width: 834px) and (device-height: 1194px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    2388,
                    1668,
                    "(device-width: 834px) and (device-height: 1194px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "10.9__iPad_Air": [
                (
                    1640,
                    2360,
                    "(device-width: 820px) and (device-height: 1180px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    2360,
                    1640,
                    "(device-width: 820px) and (device-height: 1180px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "10.5__iPad_Air": [
                (
                    1668,
                    2224,
                    "(device-width: 834px) and (device-height: 1112px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    2224,
                    1668,
                    "(device-width: 834px) and (device-height: 1112px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "10.2__iPad": [
                (
                    1620,
                    2160,
                    "(device-width: 810px) and (device-height: 1080px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    2160,
                    1620,
                    "(device-width: 810px) and (device-height: 1080px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "8.3__iPad_Mini": [
                (
                    1488,
                    2266,
                    "(device-width: 744px) and (device-height: 1133px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    2266,
                    1488,
                    "(device-width: 744px) and (device-height: 1133px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
            "9.7__iPad_Pro__7.9__iPad_mini__9.7__iPad_Air__9.7__iPad": [
                (
                    1536,
                    2048,
                    "(device-width: 768px) and (device-height: 1024px) and (-webkit-device-pixel-ratio: 2)",
                    "portrait",
                ),
                (
                    2048,
                    1536,
                    "(device-width: 768px) and (device-height: 1024px) and (-webkit-device-pixel-ratio: 2) and (orientation: landscape)",
                    "landscape",
                ),
            ],
        }

        splash_dir = (
            self.structure.root / "static" / "images" / "icons" / "splash_screens"
        )
        splash_dir.mkdir(parents=True, exist_ok=True)

        icon_image = base_icon.copy()
        icon_image.save(splash_dir / "icon.png")

        splash_lines = ["{% load static %}"]

        for device_name, orientations in splash_configs.items():
            for width, height, media, orientation in orientations:
                filename = f"{device_name}_{orientation}.png"
                splash = Image.new("RGB", (width, height), "white")
                icon_size = min(width, height) // 4
                resized_icon = icon_image.resize(
                    (icon_size, icon_size), Image.Resampling.LANCZOS
                )
                icon_x = (width - icon_size) // 2
                icon_y = (height - icon_size) // 2
                if resized_icon.mode == "RGBA":
                    splash.paste(resized_icon, (icon_x, icon_y), resized_icon)
                else:
                    splash.paste(resized_icon, (icon_x, icon_y))
                splash.save(splash_dir / filename, quality=95, optimize=True)

                splash_lines.append(
                    '<link rel="apple-touch-startup-image" media="'
                    f'{media}" href="{{% static \'images/icons/splash_screens/{filename}\' %}}">'
                )

        apple_splash_path = self.structure.root / "templates" / "apple_splash.html"
        apple_splash_path.parent.mkdir(parents=True, exist_ok=True)
        apple_splash_path.write_text("\n".join(splash_lines) + "\n")

    # ------------------------------------------------------------------
    # Manifest
    # ------------------------------------------------------------------

    def _write_manifest(self) -> None:
        ctx = self._install_context
        manifest = {
            "name": ctx.get("app_name", ""),
            "short_name": ctx.get("short_name", ""),
            "description": ctx.get("description", ""),
            "background_color": ctx.get("background_color", "#ffffff"),
            "theme_color": ctx.get("theme_color", "#000000"),
            "start_url": ctx.get("start_url", "/"),
            "dir": ctx.get("dir", "ltr"),
            "orientation": ctx.get("orientation", "portrait"),
            "display": ctx.get("display", "standalone"),
            "lang": ctx.get("language", "en"),
            "icons": self._manifest_icons,
        }
        scope = ctx.get("scope", "")
        if scope:
            manifest["scope"] = scope

        manifest_text = json.dumps(manifest, indent=4)
        content = "{%% load static %%}\n%s" % manifest_text

        manifest_path = self.structure.root / "pwa" / "templates" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(content)

    # ------------------------------------------------------------------
    # Base HTML
    # ------------------------------------------------------------------

    def _update_base_html(self) -> None:
        base_path = self.structure.base_template
        content = base_path.read_text()

        if 'rel="manifest"' in content:
            return

        manifest_link = '  <link rel="manifest" href="/manifest.json">'
        splash_path = self.structure.root / "templates" / "apple_splash.html"
        if splash_path.exists():
            replacement = (
                f"{manifest_link}\n  {{% include 'apple_splash.html' %}}\n  </head>"
            )
        else:
            replacement = f"{manifest_link}\n  </head>"

        content = content.replace("</head>", replacement)
        base_path.write_text(content)

    def _remove_from_base_html(self) -> None:
        base_path = self.structure.base_template
        if not base_path.exists():
            return
        content = base_path.read_text()

        lines = content.splitlines(keepends=True)
        filtered = [
            line
            for line in lines
            if 'rel="manifest" href="/manifest.json"' not in line
            and '{% include "apple_splash.html" %}' not in line
        ]
        base_path.write_text("".join(filtered))
