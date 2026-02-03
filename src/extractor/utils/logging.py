"""Configuração de logging estruturado."""

import logging
import sys
from typing import Any, cast

import structlog
from structlog.typing import FilteringBoundLogger


def setup_logging(debug: bool = False) -> None:
    """Configura structlog para logging estruturado."""
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if debug:
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> FilteringBoundLogger:
    """Retorna um logger configurado."""
    return cast(FilteringBoundLogger, structlog.get_logger(name))
