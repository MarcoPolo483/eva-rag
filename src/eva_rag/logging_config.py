"""
Structured logging configuration for EVA RAG.

Features:
- JSON-formatted logs
- Correlation IDs for request tracing
- Log levels per module
- Azure Application Insights integration
"""

import logging
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json
from contextvars import ContextVar
from uuid import uuid4

from pythonjsonlogger import jsonlogger


# Context variable for correlation ID (request tracing)
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_var.get() or "no-correlation-id"
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON log formatter with additional fields."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        
        # Add correlation ID
        log_record['correlation_id'] = getattr(record, 'correlation_id', 'no-correlation-id')
        
        # Add environment
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')
        
        # Add custom fields from extra
        if hasattr(record, 'extra_fields'):
            log_record.update(record.extra_fields)


def setup_logging(
    level: str = None,
    json_logs: bool = None,
    log_file: Optional[str] = None
):
    """
    Configure application logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Enable JSON-formatted logs
        log_file: Optional log file path
    """
    # Get configuration from environment
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    if json_logs is None:
        json_logs = os.getenv('JSON_LOGS', 'false').lower() == 'true'
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    # Add correlation ID filter
    console_handler.addFilter(CorrelationIdFilter())
    
    if json_logs:
        # JSON formatter
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        # Human-readable formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s (correlation_id=%(correlation_id)s)',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level))
        file_handler.addFilter(CorrelationIdFilter())
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific log levels for libraries
    logging.getLogger('azure').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.INFO)
    
    # Log startup
    root_logger.info(
        "Logging configured",
        extra={
            'extra_fields': {
                'log_level': level,
                'json_logs': json_logs,
                'log_file': log_file
            }
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set correlation ID for current context.
    
    Args:
        correlation_id: Correlation ID (generates new UUID if None)
        
    Returns:
        Correlation ID
    """
    if correlation_id is None:
        correlation_id = str(uuid4())
    
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return correlation_id_var.get()


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **kwargs
):
    """
    Log with additional context fields.
    
    Args:
        logger: Logger instance
        level: Log level (logging.INFO, etc.)
        message: Log message
        **kwargs: Additional context fields
    """
    logger.log(
        level,
        message,
        extra={'extra_fields': kwargs}
    )


# Convenience functions
def log_info(logger: logging.Logger, message: str, **kwargs):
    """Log info with context."""
    log_with_context(logger, logging.INFO, message, **kwargs)


def log_warning(logger: logging.Logger, message: str, **kwargs):
    """Log warning with context."""
    log_with_context(logger, logging.WARNING, message, **kwargs)


def log_error(logger: logging.Logger, message: str, **kwargs):
    """Log error with context."""
    log_with_context(logger, logging.ERROR, message, **kwargs)


def log_debug(logger: logging.Logger, message: str, **kwargs):
    """Log debug with context."""
    log_with_context(logger, logging.DEBUG, message, **kwargs)


# Azure Application Insights integration
def setup_app_insights(connection_string: Optional[str] = None):
    """
    Configure Azure Application Insights logging.
    
    Args:
        connection_string: App Insights connection string
    """
    connection_string = connection_string or os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
    
    if not connection_string:
        logging.warning("Application Insights connection string not configured")
        return
    
    try:
        from opencensus.ext.azure.log_exporter import AzureLogHandler
        
        logger = logging.getLogger()
        logger.addHandler(AzureLogHandler(connection_string=connection_string))
        
        logging.info("Application Insights logging configured")
        
    except ImportError:
        logging.warning("opencensus-ext-azure not installed. Skipping App Insights integration.")


# Request logging middleware helper
class RequestLogger:
    """Helper for logging HTTP requests."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """Log HTTP request."""
        log_with_context(
            self.logger,
            logging.INFO,
            f"{method} {path} {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            **kwargs
        )
    
    def log_error(
        self,
        method: str,
        path: str,
        error: Exception,
        **kwargs
    ):
        """Log HTTP error."""
        log_with_context(
            self.logger,
            logging.ERROR,
            f"{method} {path} failed: {str(error)}",
            method=method,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )
