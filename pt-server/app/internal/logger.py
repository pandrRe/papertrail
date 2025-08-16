import logging
import uuid
import json
import os
from contextvars import ContextVar
from typing import Optional
from datetime import datetime, timezone

# Request context variable for storing request ID
request_id_context: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs"""

    def format(self, record: logging.LogRecord) -> str:
        # Base log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request ID if available
        request_id = request_id_context.get()
        if request_id:
            log_entry["request_id"] = request_id

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class HumanReadableFormatter(logging.Formatter):
    """Custom formatter for human-readable console output"""

    def __init__(self):
        # Format: [TIME] [LEVEL] [REQUEST_ID] MESSAGE - extra_fields
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )

    def format(self, record: logging.LogRecord) -> str:
        # Start with base formatting
        base_msg = super().format(record)

        # Add request ID if available
        request_id = request_id_context.get()
        if request_id:
            # Insert request ID after level
            parts = base_msg.split("] ", 1)
            if len(parts) == 2:
                base_msg = f"{parts[0]}] [{request_id[:8]}] {parts[1]}"

        # Add extra fields if present
        if hasattr(record, "extra_fields") and record.extra_fields:
            extra_parts = []
            for key, value in record.extra_fields.items():
                if isinstance(value, (str, int, float, bool)):
                    extra_parts.append(f"{key}={value}")
                else:
                    extra_parts.append(f"{key}={json.dumps(value)}")

            if extra_parts:
                base_msg += f" | {', '.join(extra_parts)}"

        return base_msg


class StructuredLogger:
    """Wrapper around logging.Logger that adds structured logging capabilities"""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal logging method that adds extra fields"""
        extra = {"extra_fields": kwargs} if kwargs else {}
        self._logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs) -> None:
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self._log(logging.CRITICAL, message, **kwargs)


def generate_request_id() -> str:
    """Generate a new request ID"""
    return str(uuid.uuid4())


def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context"""
    request_id_context.set(request_id)


def get_request_id() -> Optional[str]:
    """Get the current request ID"""
    return request_id_context.get()


# Configure the logger
base_logger = logging.getLogger("papertrail")
base_logger.setLevel(logging.DEBUG)

# Create console handler with human-readable format
console_handler = logging.StreamHandler()
console_handler.setFormatter(HumanReadableFormatter())
console_handler.setLevel(logging.DEBUG)
base_logger.addHandler(console_handler)

# Create file handler with JSON format
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "papertrail.log")

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(StructuredFormatter())
file_handler.setLevel(logging.DEBUG)
base_logger.addHandler(file_handler)

# Prevent duplicate logs from uvicorn
base_logger.propagate = False

# Create structured logger instance
logger = StructuredLogger(base_logger)
