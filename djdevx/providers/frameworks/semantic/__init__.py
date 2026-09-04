from .._base import Asset, CSSFramework
from .._registry import register


@register
class SemanticFramework(CSSFramework):
    name: str = "semantic"
    display_name: str = "Semantic UI"
    description: str = "Semantic UI CSS/JS framework"
    css_assets: list[Asset] = [
        Asset(
            url="https://cdn.jsdelivr.net/npm/semantic-ui@2.5.0/dist/semantic.min.css",
            filename="semantic.min.css",
        ),
    ]
    js_assets: list[Asset] = [
        Asset(
            url="https://cdn.jsdelivr.net/npm/semantic-ui@2.5.0/dist/semantic.min.js",
            filename="semantic.min.js",
        ),
    ]
