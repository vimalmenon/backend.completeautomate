import logging
from datetime import datetime
from uuid import uuid4

from backend.config.env import env
from backend.data import TaskData, YouTubeVideoJobData
from backend.database.task.task_db import TaskDB
from backend.enum import JobEnum, PlatformEnum, TaskStatusEnum, TeamEnum
from backend.helper.start_up.start_up import StartUp
from backend.jobs import (
    BaseJob,
    ImageGeneratorJob,
    ImagePromptJob,
    NoJob,
    PromptAnalyzerJob,
    YouTubeJob,
)

logger = logging.getLogger(__name__)


class TaskSchedulerServices:
    def __init__(self):
        self.task_db = TaskDB()
        StartUp()
        self.job: dict[JobEnum, type[BaseJob]] = {
            JobEnum.YouTubeChannel: YouTubeJob,
            JobEnum.YouTubeVideo: YouTubeJob,
            JobEnum.YouTubeThumbnail: YouTubeJob,
            JobEnum.YouTubeVideoSummarize: YouTubeJob,
            JobEnum.YouTubeVideoAnalyze: YouTubeJob,
            JobEnum.YouTubeVideoDetailUpdater: YouTubeJob,
            JobEnum.PromptAnalyzer: PromptAnalyzerJob,
            JobEnum.ImageGenerator: ImageGeneratorJob,
            JobEnum.ImagePrompt: ImagePromptJob,
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

    def setup_one_time_task(self) -> TaskData:
        payload_cls = YouTubeVideoJobData(
            ref_id=f"{PlatformEnum.YouTubeVideo.value}#{env.YOUTUBE_CHANNEL_ID}"
        )
        task = TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeVideo,
            payload=payload_cls.to_json(),
            created_by=TeamEnum.OWNER,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
        )
        self.create_task(task)

    def create_task(self, task: TaskData) -> TaskData:
        self.task_db.add_task(task)
        return task

    def delete_task(self, task: TaskData) -> TaskData:
        self.task_db.delete_task(task)
        return task

    def get_tasks(self) -> list[TaskData]:
        return self.task_db.get_tasks()

    def get_task_by_id(self, task_id: str) -> TaskData | None:
        tasks = self.task_db.get_tasks()
        for task in tasks:
            if str(task.id) == task_id:
                return task
        return None

    def update_task(self, task: TaskData) -> None:
        self.task_db.update_task(task)
