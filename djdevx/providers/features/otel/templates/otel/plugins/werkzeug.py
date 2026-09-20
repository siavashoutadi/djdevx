"""OTel plugin — capture werkzeug serving and access logs.

Attaches the shared logging handler to the werkzeug logger, which
django-extensions' ``runserver_plus`` configures with ``propagate: False``
(line 410-414 of runserver_plus.py) and which would therefore never reach
the root or ``django`` loggers attached in ``otel.core``.

Activated automatically by the plugin discovery in ``otel.setup`` when the
development server is ``runserver_plus`` (the Werkzeug debugger).
"""

import logging

from otel.core import Providers


def instrument(providers: Providers) -> bool:
    handler = providers.logging_handler
    logging.getLogger("werkzeug").addHandler(handler)
    return True
