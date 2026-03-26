import logging

from backend.config.env import env
from backend.data import JobData
from backend.exception.app_exception import AppException
from backend.jobs import YouTubeChannelJob, YouTubeVideoJob
from backend.manager import ActionManager, DataManager, JobManager, StartUpManager

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self):
        self.job_manager = JobManager()
        self.startup_manager = StartUpManager()
        self.data_manager = DataManager()

    def start(
        self,
        job_id: str | None = None,
        upload: bool | None = False,
        action: str | None = None,
    ) -> None:
        if action:
            ActionManager(action).execute()
            return
        if job_id:
            logger.info("Starting one-time job execution for job_id=%s", job_id)
            self.__run_job_by_id(job_id)
            logger.info("Completed one-time job execution for job_id=%s", job_id)
            return
        if upload:
            logger.info("Starting upload script execution")
            self.__run_upload_script()
            logger.info("Completed upload script execution")
            return
        self.startup_manager.start()
        jobs = self.job_manager.get_all_active_jobs()
        for job in jobs:
            self.__run_job(job)

        self.startup_manager.end()

    def __run_job(self, job: JobData) -> None:
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

    def __run_upload_script(self) -> bool:
        if env.OFFLINE:
            return self.data_manager.upload()
        raise AppException("Upload is only available when Offline")

    def __run_job_by_id(self, job_id: str) -> None:
        job = self.job_manager.get_job_by_id(job_id)
        if job:
            self.__run_job(job)
