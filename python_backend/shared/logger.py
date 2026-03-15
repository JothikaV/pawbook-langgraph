"""
shared/logger.py
Centralized logging configuration for PawBook backend.
All loggers set to INFO level.
"""
import logging
import sys
from datetime import datetime

# Create logger format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create console handler with formatting
def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Setup a logger with console output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
