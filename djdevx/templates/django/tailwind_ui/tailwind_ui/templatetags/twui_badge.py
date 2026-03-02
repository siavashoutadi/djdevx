from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def twui_badge(type="info", text="", icon=None):
    """
    Render a badge component.

    Args:
        type: Badge type (info, success, warning, error, primary, secondary, accent, neutral)
        text: Badge text
        icon: Badge icon (optional)

    Returns:
        Rendered HTML string
    """
    ALLOWED_TYPES = [
        "primary",
        "secondary",
        "accent",
        "neutral",
        "info",
        "success",
        "warning",
        "error",
    ]
    if type not in ALLOWED_TYPES:
        type = "primary"

    context = {
        "type": type,
        "text": text,
        "icon": icon,
    }

    return render_to_string("tailwind_ui/components/base/badge.html", context)
