from datetime import datetime, timedelta
from logging import getLogger

from tabulate import tabulate

from backend.enum import JobsStatusEnum
from backend.manager.data_manager import DataManager
from backend.manager.job_manager import JobManager

logger = getLogger(__name__)


class StartUpManager:
    def start(self) -> None:
        logger.info("Starting startup manager flow")
        DataManager().start_up_script()
        self.__add_start_up_jobs()
        logger.info("Startup manager flow completed")

    def end(self) -> None:
        self.__archive_old_jobs()
        self.__show_active_jobs()

    def __add_start_up_jobs(self) -> bool:
        JobManager().create_youtube_channel_onboarding_job()
        return True

    def __archive_old_jobs(self):
        job_manager = JobManager()
        jobs = job_manager.get_all_completed_job()
        [
            job_manager.update_job_status(job_id=job.id, status=JobsStatusEnum.ARCHIVED)
            for job in jobs
            if self.__check_if_past_due_date(job.completed_at)
        ]

    def __check_if_past_due_date(self, completed_at: datetime | None) -> bool:
        if completed_at:
            delta = datetime.now() - completed_at
            return delta >= timedelta(weeks=2)
        return False

    def __show_active_jobs(self):
        jobs = JobManager().get_all_active_jobs()
        data = [[job.id, job.type, job.status] for job in jobs]
        headers = ["ID", "Type", "Status"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
