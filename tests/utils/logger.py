import logging
import logging.config
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
    # Get project root and create logs directory
    project_root = get_project_root()
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)

    # Load logging configuration
    config_path = project_root / 'tests' / 'config' / 'logging.conf'
    logging.config.fileConfig(str(config_path))

    # Get the test logger
    logger = logging.getLogger('testLogger')
    logger.info(f"Test logging initialized. Log file: {log_dir / 'tests.log'}")
    return logger

# Create a logger instance that can be imported by test files
logger = setup_logging() 