import logging

from backend.config.logging_config import setup_logging
from backend.task_scheduler_services import TaskSchedulerServices

logger = logging.getLogger(__name__)


def main():
    # Initialize logging
    setup_logging(log_dir="logs")

    logger.info("Starting Complete Automate application")
    TaskSchedulerServices().start()
    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()
