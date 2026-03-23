import argparse
import logging

from backend.config.logging_config import setup_logging
from backend.jobs_scheduler import JobScheduler

logger = logging.getLogger(__name__)


def main():
    # Initialize logging
    setup_logging(log_dir="logs")

    logger.info("Starting Complete Automate application")

    parser = argparse.ArgumentParser()

    parser.add_argument("--job-id", dest="job_id", required=False)
    parser.add_argument("--transform", dest="transform", required=False)
    parser.add_argument("--test", dest="test", required=False)
    parser.add_argument("--upload", dest="upload", required=False)

    args = parser.parse_args()

    JobScheduler().start(
        job_id=args.job_id, transform=args.transform, test=args.test, upload=args.upload
    )

    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()
