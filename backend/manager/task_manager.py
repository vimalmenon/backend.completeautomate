from datetime import datetime
from uuid import uuid4

from backend.data import (
    TaskData,
    YouTubeJobData,
    YouTubeVideoSummarizeJobData,
)
from backend.database import TaskDB
from backend.enum import JobEnum, TaskStatusEnum
from backend.exception.app_exception import AppException


class TaskManager:
    TASK_NOT_FOUND = "Task not found"

    def __init__(self, task: TaskData | None = None):
        self.task = task

    def add_task(
        self,
        task: TaskData,
    ) -> None:
        TaskDB().add_task(task)

    def get_all_active_tasks(self) -> list[TaskData]:
        return TaskDB().get_active_tasks()

    def create_youtube_analysis_task(
        self, ref_id: str, created_by: JobEnum
    ) -> TaskData:
        if not self.task:
            raise AppException(self.TASK_NOT_FOUND)
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
            raise AppException(self.TASK_NOT_FOUND)
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
        payload_cls = YouTubeJobData(ref_id=ref_id)
        return TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeChannel,
            payload=payload_cls.to_json(),
            created_by=created_by,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
            trail=[],
        )

    def create_youtube_summarize_task(
        self, ref_id: str, created_by: JobEnum
    ) -> TaskData:
        if not self.task:
            raise AppException(self.TASK_NOT_FOUND)
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
