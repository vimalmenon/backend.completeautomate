import logging
from uuid import UUID

from datatime import datetime

from backend.data import JobData
from backend.enum import JobsStatusEnum
from backend.jobs import (
    NoJob,
    PromptSuggesterJob,
    YouTubeChannelJob,
    YouTubeStatsUpdaterJob,
    YouTubeVideoJob,
)
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
        action: str | None = None,
    ) -> None:
        if action:
            ActionManager(action).execute()
            return
        if job_id:
            logger.info("Starting one-time job execution for job_id=%s", job_id)
            self.__run_job_by_id(job_id=UUID(job_id))
            logger.info("Completed one-time job execution for job_id=%s", job_id)
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
            job_response = YouTubeChannelJob(job=job).execute()
        elif job.type in YouTubeVideoJob.types:
            job_response = YouTubeVideoJob(job=job).execute()
        elif job.type in YouTubeStatsUpdaterJob.types:
            job_response = YouTubeStatsUpdaterJob(job=job).execute()
        elif job.type in PromptSuggesterJob.types:
            job_response = PromptSuggesterJob(job=job).execute()
        else:
            job_response = NoJob(job=job).execute()
        if job_response.status == JobsStatusEnum.COMPLETE:
            job.completed_at = datetime.now()
        self.job_manager.update_job_data(
            job_id=job.id,
            status=job_response.status,
            failed_count=job_response.failed_count,
            task_data=job_response.task_data,
            error_msg=job_response.error_msg,
            completed_at=job.completed_at,
            # job_response.pending_on
        )

        logger.info(
            f"Completed scheduled job execution for job_id={job.id}, type={job.type}"
        )

    def __run_job_by_id(self, job_id: UUID) -> None:
        job = self.job_manager.get_job_by_id(job_id)
        if job:
            self.__run_job(job)
