from .._base import BaseFramework
from .._registry import register


@register
class BootstrapFramework(BaseFramework):
    name: str = "bootstrap"
    display_name: str = "Bootstrap"
    description: str = "Bootstrap CSS/JS framework"
    css_url: str = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    )
    css_filename: str = "bootstrap.min.css"
    js_url: str = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
    )
    js_filename: str = "bootstrap.bundle.min.js"
