from datetime import datetime

from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum


class JobManager:

    def save_job(self, job_data: JobData):
        pass

    def add_channel_job(self, channel_id: str):
        JobData(
            status=JobsStatusEnum.IN_PROGRESS,
            type=JobTypeEnum.YouTubeChannel,
            task_data={},
            created_at=datetime.now(),
        )
        pass

    def add_video_job(self, video_id: str):
        pass

    def add_video_checker_job(self, ref_id: str):
        pass

    def add_channel_stats_updater_job(self, ref_id: str):
        pass

    def add_video_stats_updater_job(self, ref_id: str):
        pass
