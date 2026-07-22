"""Structured logging configuration for OmniRAG.

Rule R-42: log structured data, never formatted strings. Rule R-43: no
print()/console.log anywhere — everything goes through the logger
configured here. Rule R-NEW (Blueprint 2.1): every log entry carries
timestamp, level, service, correlation_id, event.

All other modules do:

    from app.shared.logger import get_logger
    logger = get_logger(__name__)
    logger.info("user.login", user_id=user.id, duration_ms=elapsed)

Never configure structlog more than once per process — call
configure_logging() exactly once, at startup (app/server.py).
"""

from __future__ import annotations

import logging
import sys

import structlog

from app.config import get_settings

_SERVICE_NAME = "omnirag-api"

_configured = False


def configure_logging() -> None:
    """Configure structlog + stdlib logging. Idempotent — safe to call
    more than once (later calls are a no-op) so importing this module
    in tests doesn't double-configure."""

    global _configured
    if _configured:
        return

    settings = get_settings()

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level.upper(),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _add_service_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelNamesMapping()[settings.log_level.upper()]
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _configured = True


def _add_service_name(
    logger: object, method_name: str, event_dict: structlog.typing.EventDict
) -> structlog.typing.EventDict:
    """Attach the fixed service name to every log entry (Rule R-NEW)."""

    event_dict["service"] = _SERVICE_NAME
    return event_dict


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound to the calling module's name.

    Ensures configure_logging() has run first — modules can safely call
    get_logger(__name__) at import time without ordering concerns,
    since configure_logging() is itself idempotent.
    """

    configure_logging()
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
