import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Global logger instance
_logger = None


def setup_logger():
    global _logger

    # If logger is already configured, return the existing instance
    if _logger is not None:
        return _logger

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Create a logger
    logger = logging.getLogger("movie_app")

    # Only configure the logger if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create a file handler that logs to a file with the current date
        log_filename = f"movie_app_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file = os.path.join("logs", log_filename)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )

        # Create a formatter and set it for the handler
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Create a stream handler for console output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Store the configured logger
    _logger = logger

    return logger
