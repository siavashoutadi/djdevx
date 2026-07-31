from .._base import BaseFramework
from .._registry import register


@register
class SemanticFramework(BaseFramework):
    name: str = "semantic"
    display_name: str = "Semantic UI"
    description: str = "Semantic UI CSS/JS framework"
    css_url: str = (
        "https://cdn.jsdelivr.net/npm/semantic-ui@2.5.0/dist/semantic.min.css"
    )
    css_filename: str = "semantic.min.css"
    js_url: str = "https://cdn.jsdelivr.net/npm/semantic-ui@2.5.0/dist/semantic.min.js"
    js_filename: str = "semantic.min.js"
