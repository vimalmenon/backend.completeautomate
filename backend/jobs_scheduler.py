import logging

from backend.jobs import YouTubeChannelJob
from backend.manager import JobManager

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self):
        self.job_manager = JobManager()

    def start(
        self,
        job_id: str | None = None,
        transform: bool | None = False,
        test: bool | None = False,
    ) -> None:
        if job_id:
            logger.info("Starting one-time job execution for job_id=%s", job_id)

            logger.info("Completed one-time job execution for job_id=%s", job_id)
            return
        if transform:
            logger.info("Starting job transformation process")

            logger.info("Completed job transformation process")
            return
        if test:
            logger.info("Starting test script execution")

            logger.info("Completed test script execution")
            return
        jobs = self.job_manager.get_all_active_jobs()
        for job in jobs:
            logger.info(
                f"Starting scheduled job execution for job_id={job.id}, type={job.type}"
            )
            if job.type in YouTubeChannelJob.types:
                YouTubeChannelJob(job=job).execute()
                # Execute YouTubeChannelJob specific logic here
                pass

            logger.info(
                f"Completed scheduled job execution for job_id={job.id}, type={job.type}"
            )
