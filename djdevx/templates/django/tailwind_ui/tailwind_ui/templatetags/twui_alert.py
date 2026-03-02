from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def twui_alert(type="info", title="", message="", show_icon=True, dismissible=False):
    """
    Render an alert component.

    Args:
        type: Alert type (info, success, warning, error)
        title: Alert title
        message: Alert message
        show_icon: Whether to show an icon
        dismissible: Whether the alert can be dismissed

    Returns:
        Rendered HTML string
    """
    ALLOWED_TYPES = ["info", "success", "warning", "error"]
    if type not in ALLOWED_TYPES:
        type = "info"

    show_icon = bool(show_icon)
    dismissible = bool(dismissible)

    context = {
        "type": type,
        "title": title,
        "message": message,
        "show_icon": show_icon,
        "dismissible": dismissible,
    }

    return render_to_string("tailwind_ui/components/base/alert.html", context)
