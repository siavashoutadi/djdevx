"""DEBUG-only view used to verify that events actually reach Sentry."""

from django.http import HttpRequest, HttpResponse


def trigger_error(request: HttpRequest) -> HttpResponse:
    """Raise a ``ZeroDivisionError`` so Sentry captures a real event.

    The result is echoed back so that a fixed copy of this view (or a
    hand-written ``1 / 0`` elsewhere) is visibly broken rather than silently
    returning a wrong number.
    """
    division_by_zero = 1 / 0
    return HttpResponse(f"unreachable: {division_by_zero}")
