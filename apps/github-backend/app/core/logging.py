"""Structured logging configuration using structlog."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.contextvars import (
    bind_contextvars,
    clear_contextvars,
    merge_contextvars,
)
from structlog.stdlib import ProcessorFormatter

from app.core.config import get_settings


def _build_processors(json_output: bool) -> list[Any]:
    """Build the structlog processor chain."""

    processors: list[Any] = [
        merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=True,
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_output:
        processors.append(
            structlog.processors.JSONRenderer()
        )
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
            )
        )

    return processors


def configure_logging() -> None:
    """Configure structlog and Python's standard logging system."""

    settings = get_settings()

    use_json = (
        settings.log_json
        or settings.is_production
    )

    log_level = getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    )

    processors = _build_processors(
        json_output=use_json
    )

    # ---------------------------------------------------------
    # Configure structlog
    # ---------------------------------------------------------

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            log_level
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # ---------------------------------------------------------
    # Configure standard library logging
    # ---------------------------------------------------------

    handler = logging.StreamHandler(
        stream=sys.stdout
    )

    formatter = ProcessorFormatter(
        processor=processors[-1],
        foreign_pre_chain=processors[:-1],
    )

    handler.setFormatter(formatter)

    # ---------------------------------------------------------
    # Configure root logger
    # ---------------------------------------------------------

    root_logger = logging.getLogger()

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # ---------------------------------------------------------
    # Reduce noisy third-party logs
    # ---------------------------------------------------------

    noisy_loggers = (
        "uvicorn.access",
        "sqlalchemy.engine.Engine",
    )

    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(
            logging.WARNING
        )


def get_logger(
    name: str | None = None,
) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger."""

    return structlog.get_logger(name)


__all__ = [
    "bind_contextvars",
    "clear_contextvars",
    "configure_logging",
    "get_logger",
]