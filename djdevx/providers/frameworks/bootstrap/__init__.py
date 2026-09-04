from .._base import Asset, CSSFramework
from .._registry import register


@register
class BootstrapFramework(CSSFramework):
    name: str = "bootstrap"
    display_name: str = "Bootstrap"
    description: str = "Bootstrap CSS/JS framework"
    css_assets: list[Asset] = [
        Asset(
            url=(
                "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/"
                "bootstrap.min.css"
            ),
            filename="bootstrap.min.css",
        ),
    ]
    js_assets: list[Asset] = [
        Asset(
            url=(
                "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/"
                "bootstrap.bundle.min.js"
            ),
            filename="bootstrap.bundle.min.js",
        ),
    ]
