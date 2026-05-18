from datetime import datetime, timedelta
from logging import getLogger

from tabulate import tabulate

from backend.enum import JobsStatusEnum
from backend.manager.data_manager import DataManager
from backend.manager.job_manager import JobManager
from backend.manager.prompt_manager import PromptManager

logger = getLogger(__name__)


class StartUpManager:
    def __init__(self):
        self.job_manager = JobManager()

    def start(self) -> None:
        logger.info("Starting startup manager flow")
        DataManager().start_up_script()
        PromptManager().seed_default_prompts()
        logger.info("Startup manager flow completed")

    def end(self) -> None:
        self.__archive_old_jobs()
        self.__remove_clean_up_jobs()
        self.__show_active_jobs()

    def __archive_old_jobs(self) -> None:
        jobs = self.job_manager.get_all_completed_job()
        [
            self.job_manager.update_job_status(
                job_id=job.id, status=JobsStatusEnum.CLEAN_UP
            )
            for job in jobs
            if self.__check_if_past_due_date(job.completed_at)
        ]

    def __remove_clean_up_jobs(self) -> None:
        jobs = self.job_manager.get_all_cleanup_job()
        for job in jobs:
            self.job_manager.delete_job(job)

    def __check_if_past_due_date(self, completed_at: datetime | None) -> bool:
        if completed_at:
            delta = datetime.now() - completed_at
            return delta >= timedelta(weeks=2)
        return False

    def __show_active_jobs(self):
        jobs = self.job_manager.get_all_active_jobs()
        data = [[job.id, job.type, job.status, job.created_at] for job in jobs]
        headers = ["ID", "Type", "Status", "Created At"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
