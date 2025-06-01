"""
Structured logging configuration for the application.
"""

# Import Rich protection first
from app.core.rich_protection import disable_rich_completely, safe_format_exception, safe_format_request
disable_rich_completely()

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
        # Ultra-minimal processors for development to completely avoid Rich recursion issues
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="%H:%M:%S"),
            # Use KeyValueRenderer instead of ConsoleRenderer to avoid Rich completely
            structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event']),
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
                # Use KeyValueRenderer instead of ConsoleRenderer to avoid Rich
                "processor": structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event']),
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
    """Log error with context, safe from Rich recursion."""
    logger = get_logger("error")
    
    # Create safe context to prevent Rich recursion
    safe_context = {}
    if context:
        for key, value in context.items():
            try:
                # Only include simple, serializable values
                if isinstance(value, (str, int, float, bool, type(None))):
                    safe_context[key] = value
                elif isinstance(value, (list, tuple)) and len(value) < 10:
                    # Only include small lists/tuples
                    safe_context[key] = str(value)[:100]  # Truncate long strings
                else:
                    safe_context[key] = f"<{type(value).__name__}>"
            except Exception:
                safe_context[key] = "<unprintable>"
    
    # Safe kwargs filtering
    safe_kwargs = {}
    for key, value in kwargs.items():
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                safe_kwargs[key] = value
            else:
                safe_kwargs[key] = f"<{type(value).__name__}>"
        except Exception:
            safe_kwargs[key] = "<unprintable>"
    
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error)[:500],  # Truncate long error messages
        context=safe_context,
        **safe_kwargs
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
    """Log security event with safe parameter handling."""
    logger = get_logger("security")
    
    # Safe kwargs filtering to prevent Rich recursion
    safe_kwargs = {}
    for key, value in kwargs.items():
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                safe_kwargs[key] = value
            else:
                safe_kwargs[key] = f"<{type(value).__name__}>"
        except Exception:
            safe_kwargs[key] = "<unprintable>"
    
    logger.warning(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent[:200] if user_agent else None,  # Truncate long user agents
        **safe_kwargs
    )


def log_request_safely(
    request,
    message: str = "Request processed",
    level: str = "info",
    **kwargs: Any
) -> None:
    """Safely log request information without causing Rich recursion."""
    logger = get_logger("request")
    
    # Extract only safe, non-circular request information
    try:
        safe_request_info = {
            "method": getattr(request, 'method', 'unknown'),
            "path": str(getattr(request, 'url', {}).path) if hasattr(request, 'url') else 'unknown',
            "client_ip": getattr(request, 'client', {}).host if hasattr(request, 'client') else 'unknown',
        }
        
        # Add headers safely
        if hasattr(request, 'headers'):
            safe_headers = {}
            for key, value in request.headers.items():
                if key.lower() not in ['authorization', 'cookie', 'x-api-key']:
                    safe_headers[key] = value[:100] if isinstance(value, str) else str(value)[:100]
            safe_request_info["headers_count"] = len(request.headers)
        
        # Safe kwargs filtering
        safe_kwargs = {}
        for key, value in kwargs.items():
            try:
                if isinstance(value, (str, int, float, bool, type(None))):
                    safe_kwargs[key] = value
                else:
                    safe_kwargs[key] = f"<{type(value).__name__}>"
            except Exception:
                safe_kwargs[key] = "<unprintable>"
        
        log_func = getattr(logger, level, logger.info)
        log_func(message, request_info=safe_request_info, **safe_kwargs)
        
    except Exception as e:
        # Fallback to minimal logging if even safe extraction fails
        logger.warning(f"Request logging failed: {e}")


def log_sync_operation(
    operation_type: str,
    shop_id: int = None,
    sync_job_id: int = None,
    status: str = None,
    items_processed: int = None,
    items_total: int = None,
    duration: float = None,
    **kwargs: Any
) -> None:
    """Log sync operation with detailed metrics."""
    logger = get_logger("sync_operation")
    
    # Safe kwargs filtering
    safe_kwargs = {}
    for key, value in kwargs.items():
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                safe_kwargs[key] = value
            else:
                safe_kwargs[key] = f"<{type(value).__name__}>"
        except Exception:
            safe_kwargs[key] = "<unprintable>"
    
    logger.info(
        "Sync operation",
        operation_type=operation_type,
        shop_id=shop_id,
        sync_job_id=sync_job_id,
        status=status,
        items_processed=items_processed,
        items_total=items_total,
        duration_seconds=duration,
        progress_percentage=round((items_processed / items_total) * 100, 2) if items_processed and items_total else None,
        **safe_kwargs
    )


def log_shopify_api_call(
    endpoint: str,
    method: str = "GET",
    shop_domain: str = None,
    status_code: int = None,
    duration: float = None,
    rate_limit_remaining: int = None,
    rate_limit_total: int = None,
    **kwargs: Any
) -> None:
    """Log Shopify API call with rate limiting info."""
    logger = get_logger("shopify_api")
    
    # Safe kwargs filtering
    safe_kwargs = {}
    for key, value in kwargs.items():
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                safe_kwargs[key] = value
            else:
                safe_kwargs[key] = f"<{type(value).__name__}>"
        except Exception:
            safe_kwargs[key] = "<unprintable>"
    
    logger.info(
        "Shopify API call",
        endpoint=endpoint,
        method=method,
        shop_domain=shop_domain,
        status_code=status_code,
        duration_ms=duration * 1000 if duration else None,
        rate_limit_remaining=rate_limit_remaining,
        rate_limit_total=rate_limit_total,
        rate_limit_usage_percentage=round(((rate_limit_total - rate_limit_remaining) / rate_limit_total) * 100, 2) if rate_limit_remaining and rate_limit_total else None,
        **safe_kwargs
    )


def log_product_sync_progress(
    shop_id: int,
    sync_job_id: int,
    products_fetched: int = None,
    variants_processed: int = None,
    variants_created: int = None,
    variants_updated: int = None,
    variants_failed: int = None,
    current_page: int = None,
    **kwargs: Any
) -> None:
    """Log product sync progress with detailed metrics."""
    logger = get_logger("product_sync")
    
    # Safe kwargs filtering
    safe_kwargs = {}
    for key, value in kwargs.items():
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                safe_kwargs[key] = value
            else:
                safe_kwargs[key] = f"<{type(value).__name__}>"
        except Exception:
            safe_kwargs[key] = "<unprintable>"
    
    logger.info(
        "Product sync progress",
        shop_id=shop_id,
        sync_job_id=sync_job_id,
        products_fetched=products_fetched,
        variants_processed=variants_processed,
        variants_created=variants_created,
        variants_updated=variants_updated,
        variants_failed=variants_failed,
        current_page=current_page,
        success_rate=round((variants_processed - variants_failed) / variants_processed * 100, 2) if variants_processed and variants_processed > 0 else None,
        **safe_kwargs
    )


def log_store_operation(
    operation_type: str,
    shop_id: int = None,
    shop_domain: str = None,
    user_id: str = None,
    status: str = None,
    duration: float = None,
    **kwargs: Any
) -> None:
    """Log store operations like connect, disconnect, etc."""
    logger = get_logger("store_operation")
    
    # Safe kwargs filtering
    safe_kwargs = {}
    for key, value in kwargs.items():
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                safe_kwargs[key] = value
            else:
                safe_kwargs[key] = f"<{type(value).__name__}>"
        except Exception:
            safe_kwargs[key] = "<unprintable>"
    
    logger.info(
        "Store operation",
        operation_type=operation_type,
        shop_id=shop_id,
        shop_domain=shop_domain,
        user_id=user_id,
        status=status,
        duration_seconds=duration,
        **safe_kwargs
    )


def log_webhook_processing(
    event_type: str,
    shop_domain: str = None,
    webhook_id: str = None,
    shopify_id: str = None,
    processing_status: str = None,
    duration: float = None,
    **kwargs: Any
) -> None:
    """Log webhook processing with detailed information."""
    logger = get_logger("webhook_processing")
    
    # Safe kwargs filtering
    safe_kwargs = {}
    for key, value in kwargs.items():
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                safe_kwargs[key] = value
            else:
                safe_kwargs[key] = f"<{type(value).__name__}>"
        except Exception:
            safe_kwargs[key] = "<unprintable>"
    
    logger.info(
        "Webhook processing",
        event_type=event_type,
        shop_domain=shop_domain,
        webhook_id=webhook_id,
        shopify_id=shopify_id,
        processing_status=processing_status,
        duration_ms=duration * 1000 if duration else None,
        **safe_kwargs
    )