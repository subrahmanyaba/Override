import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    log_file: Optional[str] = "orchestrator.log",
    level: int = logging.INFO,
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to log file (None for console-only)
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        format: Log message format
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler (always active)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(format))
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(format))
        logger.addHandler(file_handler)

    return logger

# Example usage:
if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Logger initialized successfully!")
    logger.error("This is an error demo")