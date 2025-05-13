import logging
import os
from datetime import datetime

def setup_logger(name):
    """
    Set up a logger that writes to both file and console with timestamps and separators.
    """
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplicates
    logger.handlers = []

    # Create file handler
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f'apigee_install_{current_time}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatters and add them to the handlers
    file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_formatter = logging.Formatter('%(message)s')
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_separator(logger, operation_name=None):
    """
    Add a separator line to the log with optional operation name.
    """
    separator = "-" * 80
    if operation_name:
        logger.info(f"\n{separator}")
        logger.info(f"Starting: {operation_name}")
        logger.info(separator)
    else:
        logger.info(f"\n{separator}")

def log_file_separator(logger, resource_name):
    """
    Add a clear separator between resources.
    """
    separator = "=" * 80
    logger.info(f"\n{separator}")
    logger.info(f"Processing resource: {resource_name}")
    logger.info(separator) 