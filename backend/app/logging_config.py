"""Centralized logging configuration."""

from __future__ import annotations

import logging.config


def configure_logging(log_level: str = "INFO") -> None:
    """Configure JSON structured logging with correlation ID injection."""
    normalized_level = log_level.strip().upper() or "INFO"
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "backend.app.infra.correlation.CorrelationIdFilter",
                },
            },
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.json.JsonFormatter",
                    "format": "%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "filters": ["correlation_id"],
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": normalized_level,
                "handlers": ["console"],
            },
        }
    )
