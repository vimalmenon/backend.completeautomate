from backend.data import YouTubeVideoStatsUpdateJobData
from backend.database import YouTubeVideoDB
from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator


class YouTubeVideoStatsUpdate(BaseGenerator):
    def __init__(self, job):
        super().__init__(job)
        self.task_data = YouTubeVideoStatsUpdateJobData.to_cls(job.task_data)
        self.youtube_db = YouTubeVideoDB(ref_id=self.task_data.ref_id)
        self.channel_id = self.task_data.platform.channel_id

    def generate(self) -> tuple[JobsStatusEnum, dict]:
        videos = self.youtube_db.fetch_videos_by_channel(secondary=self.channel_id)
        for video in videos:
            if video.past_update_time(days=3):
                return JobsStatusEnum.IN_PROGRESS, self.task_data.to_json()
        return JobsStatusEnum.IN_PROGRESS, self.task_data.to_json()
