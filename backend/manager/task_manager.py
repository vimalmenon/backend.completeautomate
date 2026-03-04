from datetime import datetime
from uuid import uuid4

from backend.data import TaskData, YouTubeVideoJobData, YouTubeVideoSummarizeJobData
from backend.database import TaskDB
from backend.enum import JobEnum, TaskStatusEnum, TeamEnum


class TaskManager:

    def add_task(
        self,
        task: TaskData,
    ) -> None:
        TaskDB().add_task(task)

    def create_youtube_analysis_task(
        self, ref_id: str, created_by: TeamEnum | JobEnum, trail=[]
    ) -> TaskData:
        payload_cls = YouTubeVideoSummarizeJobData(ref_id=ref_id)
        return TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeVideoMetadataSuggester,
            payload=payload_cls.to_json(),
            created_by=created_by,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
            trail=trail,
        )

    def create_youtube_video_task(
        self, ref_id: str, created_by: TeamEnum | JobEnum, trail=[]
    ) -> TaskData:
        payload_cls = YouTubeVideoJobData(ref_id=ref_id)
        return TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeVideo,
            payload=payload_cls.to_json(),
            created_by=created_by,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
            trail=trail,
        )

    def create_youtube_summarize_task(
        self, ref_id: str, created_by: TeamEnum | JobEnum, trail=[]
    ) -> TaskData:
        job = YouTubeVideoSummarizeJobData(
            ref_id=ref_id,
        )
        return TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeVideoSummarize,
            payload=job.to_json(),
            created_by=created_by,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
            trail=trail,
        )
