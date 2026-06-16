from __future__ import annotations

import logging

import structlog

from src.config import settings

_configured = False


def configure_logging() -> None:
    """Configure structlog + stdlib logging once, emitting JSON in production.

    Binds a contextvars-backed merger so ``bind_contextvars(job_id=...)`` flows
    into every log line within a task's context without threading the value
    through call signatures.
    """
    global _configured
    if _configured:
        return

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer = (
        structlog.processors.JSONRenderer()
        if settings.log_json
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=level, format="%(message)s")
    _configured = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    configure_logging()
    return structlog.get_logger(name)


def bind_job(job_id: str, **extra: object) -> None:
    """Bind job context for the current async task so all logs carry the job_id."""
    structlog.contextvars.bind_contextvars(job_id=job_id, **extra)


def clear_job_context() -> None:
    structlog.contextvars.clear_contextvars()
