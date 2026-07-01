"""
Logging configuration for CRMS backend.
Sets up structured logging with rotation and formatting.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from .config import get_settings
from .exceptions import ConfigurationError


def setup_logging(
    log_level: Optional[str] = None,
    log_path: Optional[str] = None,
    log_rotation: Optional[str] = None,
    log_retention: Optional[str] = None,
) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_path: Path to log files directory
        log_rotation: Log rotation size (e.g., "10 MB")
        log_retention: Log retention period (e.g., "30 days")

    Raises:
        ConfigurationError: If logging configuration is invalid
    """
    try:
        settings = get_settings()

        # Use provided values or fall back to settings
        level = log_level or settings.logging.log_level
        path = log_path or settings.logging.log_path
        rotation = log_rotation or settings.logging.log_rotation
        retention = log_retention or settings.logging.log_retention

        # Ensure log directory exists
        log_dir = Path(path)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Remove default handler
        logger.remove()

        # Console handler with formatting
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stderr,
            format=console_format,
            level=level,
            colorize=True,
        )

        # File handler for general logs
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | " "{name}:{function}:{line} - {message}"
        )
        logger.add(
            log_dir / "crms_{time:YYYY-MM-DD}.log",
            format=file_format,
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
        )

        # File handler for errors only
        error_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | " "{name}:{function}:{line} - {message}"
        )
        logger.add(
            log_dir / "crms_errors_{time:YYYY-MM-DD}.log",
            format=error_format,
            level="ERROR",
            rotation=rotation,
            retention=retention,
            compression="zip",
        )

        logger.info(f"Logging configured: level={level}, path={log_dir}")

    except Exception as e:
        raise ConfigurationError(f"Failed to configure logging: {str(e)}")


def get_logger(name: str) -> object:
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
