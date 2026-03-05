import logging
from datetime import datetime

from backend.enum import JobEnum, TaskStatusEnum
from backend.jobs import (
    BaseJob,
    ImageGeneratorJob,
    ImagePromptJob,
    NoJob,
    PromptSuggesterJob,
    YouTubeJob,
)
from backend.manager import StartUpManager, TaskManager

logger = logging.getLogger(__name__)


class TaskSchedulerServices:
    def __init__(self):
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
        task_manager = TaskManager()
        tasks = task_manager.get_active_tasks()
        for task in tasks:
            job_class = self.job.get(task.job_type, NoJob)
            status, failed_count = job_class(task).execute()
            task.status = status
            task.failed_count = failed_count
            if status == TaskStatusEnum.COMPLETED:
                task.completed_at = datetime.now()
            logger.info("Task %s executed with status: %s", task.id, status)
            task_manager.update_task(task)

        task_manager.promote_new_task()
        task_manager.cleanup_tasks()
