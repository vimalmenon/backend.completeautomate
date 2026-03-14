from datetime import datetime

from backend.data import JobData, YouTubeChannelTaskData, YouTubeVideoTaskData
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
            description=f"Processing YouTube channel with ID: {channel_id}",
            task_data=task_cls.to_dict(),
            created_at=datetime.now(),
        )

    def add_video_job(self, channel_id: str, video_id: str) -> JobData:
        task_cls = YouTubeVideoTaskData(channel_id=channel_id, video_id=video_id)
        return JobData(
            status=JobsStatusEnum.IN_PROGRESS,
            type=JobTypeEnum.YouTubeVideo,
            description=f"Processing YouTube video with ID: {video_id} from channel ID: {channel_id}",
            task_data=task_cls.to_dict(),
            created_at=datetime.now(),
        )

    def add_video_checker_job(self, ref_id: str) -> JobData:
        return JobData(
            status=JobsStatusEnum.IN_PROGRESS,
            type=JobTypeEnum.YouTubeVideoChecker,
            description=f"Checking video with ref ID: {ref_id}",
            task_data={},
            created_at=datetime.now(),
        )

    def add_channel_stats_updater_job(self, ref_id: str) -> JobData:
        return JobData(
            status=JobsStatusEnum.IN_PROGRESS,
            type=JobTypeEnum.YouTubeChannelStatsUpdater,
            description=f"Updating stats for channel with ref ID: {ref_id}",
            task_data={},
            created_at=datetime.now(),
        )

    def add_video_stats_updater_job(self, ref_id: str) -> JobData:
        return JobData(
            status=JobsStatusEnum.IN_PROGRESS,
            type=JobTypeEnum.YouTubeVideoStatsUpdater,
            description=f"Updating stats for video with ref ID: {ref_id}",
            task_data={},
            created_at=datetime.now(),
        )
