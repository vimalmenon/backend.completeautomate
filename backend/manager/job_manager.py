from datetime import datetime

from backend.data import JobData, YouTubeChannelTaskData
from backend.database import JobDB
from backend.enum import JobsStatusEnum, JobTypeEnum


class JobManager:

    def save_job(self, job_data: JobData):
        JobDB().save_data(job_data)

    def add_channel_job(self, channel_id: str) -> JobData:
        task_cls = YouTubeChannelTaskData(channel_id=channel_id)
        return JobData(
            status=JobsStatusEnum.IN_PROGRESS,
            type=JobTypeEnum.YouTubeChannel,
            task_data=task_cls.to_dict(),
            created_at=datetime.now(),
        )

    def add_video_job(self, video_id: str) -> JobData:
        task_cls = YouTubeVideoTaskData(video_id=video_id)
        return JobData(
            status=JobsStatusEnum.IN_PROGRESS,
            type=JobTypeEnum.YouTubeVideo,
            task_data=task_cls.to_dict(),
            created_at=datetime.now(),
        )

    def add_video_checker_job(self, ref_id: str):
        pass

    def add_channel_stats_updater_job(self, ref_id: str):
        pass

    def add_video_stats_updater_job(self, ref_id: str):
        pass
