"""
Logging utility for the Neuralk API service.
Provides consistent logging configuration across all components.
"""

import logging
import logging.handlers
import os
from datetime import datetime

from src.utils.config import LOG_LEVEL

os.makedirs("logs", exist_ok=True)

# Logging levels mapping for configuration
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
log_level = LOG_LEVELS.get(LOG_LEVEL, logging.INFO)

log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name):
    """
    Returns a configured logger instance for the given name.
    
    Parameters:
    ----------
    name : str
        The name of the logger, typically __name__ from the calling module.
        
    Returns:
    -------
    logging.Logger
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Prevent adding duplicate handlers if logger already exists
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
        
        # File handler w/ daily rotating log files
        log_file = f"logs/{datetime.now().strftime('%Y-%m-%d')}-{name}.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file, when="midnight", backupCount=7
        )
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    
    return logger
