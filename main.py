import argparse
import logging

from backend.config.logging_config import setup_logging
from backend.task_scheduler_services import TaskSchedulerServices

logger = logging.getLogger(__name__)


def main():
    # Initialize logging
    setup_logging(log_dir="logs")

    logger.info("Starting Complete Automate application")

    parser = argparse.ArgumentParser()

    parser.add_argument("--task-id", dest="task_id", required=False)
    parser.add_argument("--transform", dest="transform", required=False)
    args = parser.parse_args()

    TaskSchedulerServices().start(task_id=args.task_id, transform=args.transform)

    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()
