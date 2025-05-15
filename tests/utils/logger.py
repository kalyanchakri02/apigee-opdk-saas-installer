import logging
import os
from pathlib import Path

def get_project_root():
    """Get the project root directory."""
    # Start from the current file's directory
    current_dir = Path(__file__).resolve().parent
    # Go up until we find setup.py
    while current_dir.parent != current_dir:  # while we haven't hit the root directory
        if (current_dir / 'setup.py').exists():
            return current_dir
        current_dir = current_dir.parent
    raise FileNotFoundError("Could not find project root (no setup.py found)")

def setup_logging():
    """Set up logging configuration for tests"""
    # Create logger
    logger = logging.getLogger('testLogger')
    logger.setLevel(logging.DEBUG)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Create logs directory in project root
    project_root = get_project_root()
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create handlers
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler
    log_file = log_dir / 'tests.log'
    file_handler = logging.FileHandler(str(log_file))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger

# Create a logger instance that can be imported by test files
logger = setup_logging() 