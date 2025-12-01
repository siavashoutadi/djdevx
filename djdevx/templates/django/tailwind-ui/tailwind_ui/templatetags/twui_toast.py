import uuid

from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def twui_toast(
    type="info",
    title="",
    message="",
    show_icon=True,
    dismissible=False,
    auto_dismiss_delay=5000,
):
    """
    Render a toast component.

    Args:
        type: Toast type (info, success, warning, error)
        title: Alert title
        message: Alert message
        show_icon: Whether to show an icon
        dismissible: Whether the toast can be dismissed
        auto_dismiss_delay: Time in milliseconds before auto-dismissing

    Returns:
        Rendered HTML string
    """
    ALLOWED_TYPES = ["info", "success", "warning", "error"]
    if type not in ALLOWED_TYPES:
        type = "info"

    show_icon = bool(show_icon)
    dismissible = bool(dismissible)

    # Generate a unique ID for this toast
    unique_id = str(uuid.uuid4())[:8]

    context = {
        "type": type,
        "title": title,
        "message": message,
        "show_icon": show_icon,
        "dismissible": dismissible,
        "unique_id": unique_id,
        "auto_dismiss_delay": auto_dismiss_delay,
    }

    return render_to_string("tailwind_ui/components/base/toast.html", context)
