from .._base import Asset, CSSFramework
from .._registry import register


@register
class FrankenUIFramework(CSSFramework):
    name: str = "frankenui"
    display_name: str = "Franken UI"
    description: str = "Franken UI CSS/JS framework"
    css_assets: list[Asset] = [
        Asset(
            url="https://cdn.jsdelivr.net/npm/franken-ui@2.1.2/dist/css/core.min.css",
            filename="franken-core.css",
        ),
        Asset(
            url=(
                "https://cdn.jsdelivr.net/npm/"
                "franken-ui@2.1.2/dist/css/utilities.min.css"
            ),
            filename="franken-utilities.css",
        ),
    ]
    js_assets: list[Asset] = [
        Asset(
            url="https://cdn.jsdelivr.net/npm/franken-ui@2.1.2/dist/js/core.iife.js",
            filename="franken-core.js",
        ),
        Asset(
            url="https://cdn.jsdelivr.net/npm/franken-ui@2.1.2/dist/js/icon.iife.js",
            filename="franken-icon.js",
        ),
    ]
    js_module: bool = True
