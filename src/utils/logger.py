"""
Logging utilities for the API.
"""

import logging
import sys
from typing import Optional

from src.common.config import settings

def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically the module name)
        log_level: Optional log level override (defaults to settings.LOG_LEVEL)

    Returns:
        Configured logger instance
    """
    log_level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(settings.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.propagate = False

    logger.setLevel(numeric_level)
    return logger
