import logging
from datetime import datetime

from backend.data import TaskData
from backend.enum import JobEnum, TaskStatusEnum
from backend.jobs import (
    BaseJob,
    ImageGeneratorJob,
    NoJob,
    PromptSuggesterJob,
    TwitterJob,
    YouTubeJob,
)
from backend.manager import StartUpManager, TaskManager

logger = logging.getLogger(__name__)


class TaskSchedulerServices:
    def __init__(self):
        self.task_manager = TaskManager()
        StartUpManager().start()
        self.job: dict[JobEnum, type[BaseJob]] = {
            JobEnum.YouTubeChannel: YouTubeJob,
            JobEnum.YouTubeVideo: YouTubeJob,
            JobEnum.YouTubeThumbnailUpdater: YouTubeJob,
            JobEnum.YouTubeVideoSummarizer: YouTubeJob,
            JobEnum.YouTubeVideoMetadataSuggester: YouTubeJob,
            JobEnum.YouTubeVideoMetadataUpdater: YouTubeJob,
            JobEnum.YouTubeVideoThumbnailPromptSuggester: YouTubeJob,
            JobEnum.ImageGenerator: ImageGeneratorJob,
            JobEnum.TwitterPost: TwitterJob,
            JobEnum.PromptSuggester: PromptSuggesterJob,
        }

    def start(
        self,
        task_id: str | None = None,
        transform: bool | None = False,
        test: bool | None = False,
    ) -> None:
        if task_id:
            logger.info("Starting one-time task execution for task_id=%s", task_id)
            self.__run_task_by_id(task_id)
            logger.info("Completed one-time task execution for task_id=%s", task_id)
            return
        if transform:
            logger.info("Starting task transformation process")
            self.task_manager.transform_tasks()
            logger.info("Completed task transformation process")
            return
        if test:
            logger.info("Starting test script execution")
            self.__run_test_script()
            logger.info("Completed test script execution")
            return
        tasks = self.task_manager.get_active_tasks()
        parallel_tasks = []
        for task in tasks:
            if task.payload.get("is_agent"):
                parallel_tasks.append(task)
            self.__run_task(task)
        self.__run_in_parallel(parallel_tasks)
        self.task_manager.promote_new_task()
        self.task_manager.cleanup_tasks()

    def __run_task_by_id(self, task_id: str) -> None:
        task_manager = TaskManager()
        logger.debug("Fetching one-time task by task_id=%s", task_id)
        task = task_manager.get_task_by_id(task_id)
        logger.info(
            "Executing one-time task: id=%s job_type=%s", task.id, task.job_type
        )
        self.__run_task(task)

    def __run_task(self, task: TaskData) -> None:
        job_class = self.job.get(task.job_type, NoJob)
        status, failed_count = job_class(task).execute()
        task.status = status
        task.failed_count = failed_count
        if status == TaskStatusEnum.COMPLETED:
            task.completed_at = datetime.now()
        logger.info("Task %s executed with status: %s", task.id, status)
        self.task_manager.update_task(task)

    def __run_test_script(self) -> bool:
        return False

    def __run_in_parallel(self, parallel_tasks: list) -> bool:
        # TODO Need to implement
        return False
