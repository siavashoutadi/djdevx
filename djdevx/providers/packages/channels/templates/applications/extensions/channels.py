"""Channels server extension — adds websocket routing to the ASGI app."""

from collections.abc import Callable
from typing import Any

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator


def load(application: Callable[..., Any]) -> None:
    import applications.asgi as asgi_module

    from ws_urls import websocket_urlpatterns

    asgi_module.application = ProtocolTypeRouter(
        {
            "http": asgi_module.application,
            "websocket": AllowedHostsOriginValidator(
                AuthMiddlewareStack(URLRouter(websocket_urlpatterns))  # type: ignore[arg-type]
            ),
        }
    )
