from .._base import CSSFramework
from .._registry import register


@register
class FrankenUIFramework(CSSFramework):
    name: str = "frankenui"
    display_name: str = "Franken UI"
    description: str = "Franken UI CSS/JS framework"
    css_url: str = (
        "https://cdn.jsdelivr.net/npm/franken-ui@1.0.3/dist/css/franken-ui.min.css"
    )
    css_filename: str = "franken.css"
    js_url: str = (
        "https://cdn.jsdelivr.net/npm/franken-ui@1.0.3/dist/js/franken-ui.min.js"
    )
    js_filename: str = "franken.js"
    js_module: bool = True
