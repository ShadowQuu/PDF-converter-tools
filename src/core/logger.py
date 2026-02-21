"""
Logging configuration module for PDF tool.
Provides centralized logging configuration for all modules.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_level=logging.INFO, log_to_file=True, log_to_console=True):
    """
    Setup centralized logging configuration.
    
    Args:
        log_level: Logging level (default: logging.INFO)
        log_to_file: Whether to log to file (default: True)
        log_to_console: Whether to log to console (default: True)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path.home() / ".pdf_tool" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate log filename with current date
    log_filename = f"pdf_tool_{datetime.now().strftime('%Y%m%d')}.log"
    log_filepath = log_dir / log_filename
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add file handler
    if log_to_file:
        file_handler = logging.FileHandler(
            log_filepath,
            encoding='utf-8',
            mode='a'  # Append mode
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Add console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    return root_logger


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


# Initialize logging on module import
setup_logging()
