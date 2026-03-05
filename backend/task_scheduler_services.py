import logging
from datetime import datetime

from backend.data import TaskData
from backend.database.task.task_db import TaskDB
from backend.enum import JobEnum, TaskStatusEnum
from backend.jobs import (
    BaseJob,
    ImageGeneratorJob,
    ImagePromptJob,
    NoJob,
    PromptSuggesterJob,
    YouTubeJob,
)
from backend.manager import StartUpManager

logger = logging.getLogger(__name__)


class TaskSchedulerServices:
    def __init__(self):
        self.task_db = TaskDB()
        StartUpManager().start()
        self.job: dict[JobEnum, type[BaseJob]] = {
            JobEnum.YouTubeChannel: YouTubeJob,
            JobEnum.YouTubeVideo: YouTubeJob,
            JobEnum.YouTubeThumbnailUpdater: YouTubeJob,
            JobEnum.YouTubeVideoSummarizer: YouTubeJob,
            JobEnum.YouTubeVideoMetadataSuggester: YouTubeJob,
            JobEnum.YouTubeVideoMetadataUpdater: YouTubeJob,
            JobEnum.ImageGenerator: ImageGeneratorJob,
            JobEnum.ImagePrompt: ImagePromptJob,
            JobEnum.PromptSuggester: PromptSuggesterJob,
        }

    def start(self) -> None:
        tasks = self.task_db.get_active_tasks()
        for task in tasks:
            job_class = self.job.get(task.job_type, NoJob)
            status, failed_count = job_class(task).execute()
            task.status = status
            task.failed_count = failed_count
            if status == TaskStatusEnum.COMPLETED:
                task.completed_at = datetime.now()
            logger.info("Task %s executed with status: %s", task.id, status)
            self.task_db.update_task(task)
        self.task_db.cleanup_tasks()

    def delete_task(self, task: TaskData) -> TaskData:
        self.task_db.delete_task(task)
        return task

    def get_tasks(self) -> list[TaskData]:
        return self.task_db.get_tasks()

    def update_task(self, task: TaskData) -> None:
        self.task_db.update_task(task)
