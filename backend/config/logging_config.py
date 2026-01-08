import logging
import logging.handlers
from pathlib import Path


def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO) -> None:
    """
    Configure logging to both file and console.

    Args:
        log_dir: Directory to store log files
        log_level: Logging level (default: logging.INFO)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Define log file paths
    main_log_file = log_path / "app.log"
    error_log_file = log_path / "errors.log"

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler - INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(detailed_formatter)

    # File handler - INFO and above with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)

    # Error file handler - ERROR and above with rotation
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured. Log files: {main_log_file}, {error_log_file}")
