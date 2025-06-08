import logging
import os
from datetime import datetime

# Singleton instance of deployment logger
_deployment_logger = None

def get_deployment_logger(log_dir: str = './') -> logging.Logger:
    """
    Get or create a singleton instance of the deployment status logger.
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        logging.Logger: Singleton deployment logger instance
    """
    global _deployment_logger
    
    if _deployment_logger is None:
        # Create logs directory if it doesn't exist
        log_dir = log_dir + '/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create a logger
        _deployment_logger = logging.getLogger('deployment_status')
        _deployment_logger.setLevel(logging.INFO)

        # Remove any existing handlers to avoid duplicates
        _deployment_logger.handlers = []

        # Create file handler for deployment status
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f'deployment_status_{current_time}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Create a simple formatter that only shows timestamp and message
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        _deployment_logger.addHandler(file_handler)
    
    return _deployment_logger

def setup_logger(name: str, log_dir: str = './') -> logging.Logger:
    """
    Set up a logger that writes to both file and console with timestamps and separators.
    
    Args:
        name: Name of the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = log_dir + '/logs'
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
    console_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to the handlers
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', 
                                     datefmt='%Y-%m-%d %H:%M:%S')
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                        datefmt='%Y-%m-%d %H:%M:%S')
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_separator(logger: logging.Logger, message: str):
    """Log a message with a separator line."""
    logger.info("=" * 80)
    logger.info(message)
    logger.info("=" * 80)

def log_file_separator(logger: logging.Logger, message: str):
    """Log a message with a file separator line."""
    logger.info("-" * 80)
    logger.info(message)
    logger.info("-" * 80)

def log_deployment_status(resource_type: str, resource_name: str, env: str, status: str, message: str = ""):
    """
    Log the deployment status of a resource using the singleton deployment logger.
    
    Args:
        resource_type: Type of resource (e.g., 'KVM', 'Proxy', etc.)
        resource_name: Name of the resource
        env: Environment name
        status: Status of deployment ('SUCCESS' or 'FAILURE')
        message: Additional message (optional)
    """
    logger = get_deployment_logger()
    status_msg = f"{resource_type} '{resource_name}' in {env}: {status}"
    if message:
        status_msg += f" - {message}"
    logger.info(status_msg) 