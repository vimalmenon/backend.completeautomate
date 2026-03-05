from datetime import datetime
from logging import getLogger
from uuid import uuid4

from backend.data import (
    TaskData,
    YouTubeJobData,
    YouTubeVideoSummarizeJobData,
)
from backend.database import TaskDB
from backend.enum import JobEnum, TaskStatusEnum
from backend.exception.app_exception import AppException

logger = getLogger(__name__)


class TaskManager:
    TASK_NOT_FOUND = "Task not found"

    def __init__(self, task: TaskData | None = None):
        logger.debug(
            f"Initializing TaskManager with task: {task.id if task else 'None'}"
        )
        self.task = task
        self.db = TaskDB()

    def add_task(
        self,
        task: TaskData,
    ) -> None:
        logger.info(f"Adding task: job_type={task.job_type}")
        TaskDB().add_task(task)

    def get_all_active_tasks(self) -> list[TaskData]:
        logger.debug("Fetching all active tasks")
        tasks = TaskDB().get_active_tasks()
        logger.debug(f"Fetched active tasks count: {len(tasks)}")
        return tasks

    def create_youtube_analysis_task(
        self, ref_id: str, created_by: JobEnum
    ) -> TaskData:
        if not self.task:
            logger.warning("Cannot create YouTube analysis task: source task missing")
            raise AppException(self.TASK_NOT_FOUND)
        logger.debug(f"Creating YouTube analysis task for ref_id={ref_id}")
        payload_cls = YouTubeVideoSummarizeJobData(ref_id=ref_id)
        return TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeVideoMetadataSuggester,
            payload=payload_cls.to_json(),
            created_by=created_by,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
            trail=self.task.trail + [self.task.id],
        )

    def create_youtube_video_task(self, ref_id: str, created_by: JobEnum) -> TaskData:
        if not self.task:
            logger.warning("Cannot create YouTube video task: source task missing")
            raise AppException(self.TASK_NOT_FOUND)
        logger.debug(f"Creating YouTube video task for ref_id={ref_id}")
        payload_cls = YouTubeJobData(ref_id=ref_id)
        return TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeVideo,
            payload=payload_cls.to_json(),
            created_by=created_by,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
            trail=[],
        )

    def create_youtube_channel_task(self, ref_id: str, created_by: JobEnum) -> TaskData:
        logger.debug(f"Creating YouTube channel task for ref_id={ref_id}")
        payload_cls = YouTubeJobData(ref_id=ref_id)
        return TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeChannel,
            payload=payload_cls.to_json(),
            created_by=created_by,
            created_at=datetime.now(),
            status=TaskStatusEnum.NEW,
            trail=[],
        )

    def create_youtube_summarize_task(
        self, ref_id: str, created_by: JobEnum
    ) -> TaskData:
        if not self.task:
            logger.warning("Cannot create YouTube summarize task: source task missing")
            raise AppException(self.TASK_NOT_FOUND)
        logger.debug(f"Creating YouTube summarize task for ref_id={ref_id}")
        job = YouTubeVideoSummarizeJobData(
            ref_id=ref_id,
        )
        return TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeVideoSummarizer,
            payload=job.to_json(),
            created_by=created_by,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
            trail=self.task.trail + [self.task.id],
        )

    def promote_new_task(self):
        logger.info("Promoting NEW tasks to IN_PROGRESS status")
        tasks = self.db.query_items(TaskStatusEnum.NEW)
        logger.debug(f"Found {len(tasks)} NEW tasks to promote")
        [self.__move_new_to_in_progress(task) for task in tasks]

    def __move_new_to_in_progress(self, task: TaskData):
        logger.info(
            f"Promoting task to IN_PROGRESS: id={task.id}, job_type={task.job_type}"
        )
        task.status = TaskStatusEnum.IN_PROGRESS
        self.db.update_task(task)

    def cleanup_tasks(self):
        logger.info("Starting cleanup of tasks with CLEAN_UP status")
        tasks = self.db.query_items(TaskStatusEnum.CLEAN_UP)
        logger.info(f"Found {len(tasks)} tasks to clean up")
        [self.db.delete_task(task) for task in tasks]
        logger.info("Task cleanup completed")

    def update_task(self, task: TaskData):
        logger.info(f"Updating task with id: {task.id}")
        self.db.update_task(task)

    def get_active_tasks(self) -> list[TaskData]:
        logger.info("Fetching active tasks")
        return self.db.get_active_tasks()
