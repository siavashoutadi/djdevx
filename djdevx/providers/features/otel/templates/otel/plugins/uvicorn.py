"""OTel plugin — capture uvicorn access and error logs.

Attaches the shared logging handler to the uvicorn loggers, which are
configured with ``propagate: False`` by uvicorn and therefore never reach
the root or ``django`` loggers attached in ``otel.core``.

Activated automatically by the plugin discovery in ``otel.setup`` when
the application is served by uvicorn (e.g. in Docker / production).
"""

import logging

from otel.core import Providers


def instrument(providers: Providers) -> bool:
    handler = providers.logging_handler
    logging.getLogger("uvicorn").addHandler(handler)
    logging.getLogger("uvicorn.error").addHandler(handler)
    logging.getLogger("uvicorn.access").addHandler(handler)
    return True
