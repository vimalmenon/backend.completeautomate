from datetime import datetime, timedelta
from logging import getLogger

from tabulate import tabulate

from backend.data import S3Data
from backend.enum import JobsStatusEnum
from backend.helper.folder_helper.folder_helper import FolderHelper
from backend.integration.storage.s3_storage import S3Storage
from backend.manager.job_manager import JobManager

logger = getLogger(__name__)


class StartUpManager:
    def start(self) -> None:
        logger.info("Starting startup manager flow")
        self.__add_start_up_file()
        self.__add_start_up_jobs()
        logger.info("Startup manager flow completed")

    def end(self) -> None:
        self.__archive_old_jobs()
        self.__sync_youtube_channels()
        self.__sync_youtube_videos()
        self.__show_active_jobs()

    def __add_start_up_file(self) -> None:
        for path in ["pickle/token.pickle", "json/client_secret.json"]:
            data = S3Data.to_cls_from_path(path)
            if not FolderHelper().check_if_file_exists(data.downloaded_path):
                logger.info(f"Startup file missing locally, downloading: {path}")
                S3Storage().download_data(data)
            else:
                logger.debug(f"Startup file already present: {path}")

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
