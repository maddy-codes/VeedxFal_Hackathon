"""
Structured logging configuration for the application.
"""

import logging
import logging.config
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging() -> None:
    """Setup structured logging configuration."""
    
    # Configure structlog with minimal processors for development
    if settings.is_production:
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Minimal processors for development to avoid Rich recursion issues
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="%H:%M:%S"),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=False, exception_formatter=structlog.dev.plain_traceback),
        ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "json" if settings.is_production else "console",
                "level": settings.LOG_LEVEL,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "WARNING" if not settings.is_production else settings.LOG_LEVEL,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "ERROR",  # Disable access logs in development
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "ERROR",  # Only show SQL errors
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False,
            },
            "httpx": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False,
            },
            "app": {
                "handlers": ["console"],
                "level": "WARNING" if not settings.is_production else "INFO",
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)
    
    # Setup Sentry if configured
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            integrations=[
                FastApiIntegration(auto_enable=True),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1 if settings.is_production else 1.0,
            send_default_pii=False,
        )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """Log function call with parameters."""
    logger = get_logger("function_call")
    logger.info(f"Calling {func_name}", **kwargs)


def log_external_api_call(
    service: str,
    endpoint: str,
    method: str = "GET",
    status_code: int = None,
    duration: float = None,
    **kwargs: Any
) -> None:
    """Log external API call."""
    logger = get_logger("external_api")
    logger.info(
        "External API call",
        service=service,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        duration_ms=duration * 1000 if duration else None,
        **kwargs
    )


def log_database_query(
    query_type: str,
    table: str = None,
    duration: float = None,
    rows_affected: int = None,
    **kwargs: Any
) -> None:
    """Log database query."""
    logger = get_logger("database")
    logger.info(
        "Database query",
        query_type=query_type,
        table=table,
        duration_ms=duration * 1000 if duration else None,
        rows_affected=rows_affected,
        **kwargs
    )


def log_business_event(
    event_type: str,
    user_id: str = None,
    shop_id: int = None,
    **kwargs: Any
) -> None:
    """Log business event."""
    logger = get_logger("business_event")
    logger.info(
        "Business event",
        event_type=event_type,
        user_id=user_id,
        shop_id=shop_id,
        **kwargs
    )


def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    **kwargs: Any
) -> None:
    """Log error with context."""
    logger = get_logger("error")
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        **kwargs,
        exc_info=True
    )


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = "ms",
    **kwargs: Any
) -> None:
    """Log performance metric."""
    logger = get_logger("performance")
    logger.info(
        "Performance metric",
        metric_name=metric_name,
        value=value,
        unit=unit,
        **kwargs
    )


def log_security_event(
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    user_agent: str = None,
    **kwargs: Any
) -> None:
    """Log security event."""
    logger = get_logger("security")
    logger.warning(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        **kwargs
    )