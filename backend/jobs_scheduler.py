import logging

from backend.jobs import YouTubeChannelJob, YouTubeVideoJob
from backend.manager import JobManager, StartUpManager

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self):
        self.job_manager = JobManager()
        self.startup_manager = StartUpManager()

    def start(
        self,
        job_id: str | None = None,
        transform: bool | None = False,
        test: bool | None = False,
    ) -> None:
        if job_id:
            logger.info("Starting one-time job execution for job_id=%s", job_id)
            self.__run_job_by_id(job_id)
            logger.info("Completed one-time job execution for job_id=%s", job_id)
            return
        if transform:
            logger.info("Starting job transformation process")
            self.__transform_data()
            logger.info("Completed job transformation process")
            return
        if test:
            logger.info("Starting test script execution")

            logger.info("Completed test script execution")
            return
        self.startup_manager.start()
        jobs = self.job_manager.get_all_active_jobs()
        for job in jobs:
            logger.info(
                f"Starting scheduled job execution for job_id={job.id}, type={job.type}"
            )
            if job.type in YouTubeChannelJob.types:
                (
                    status,
                    failed_count,
                    task_data,
                ) = YouTubeChannelJob(job=job).execute()
            elif job.type in YouTubeVideoJob.types:
                (
                    status,
                    failed_count,
                    task_data,
                ) = YouTubeVideoJob(job=job).execute()
            self.job_manager.update_job_data(
                job_id=job.id,
                status=status,
                failed_count=failed_count,
                task_data=task_data,
            )

            logger.info(
                f"Completed scheduled job execution for job_id={job.id}, type={job.type}"
            )

        self.startup_manager.end()

    def __transform_data(self) -> bool:
        # Need to add when there is some transfrom data
        return False

    def __run_job_by_id(self, job_id: str) -> None:
        pass
