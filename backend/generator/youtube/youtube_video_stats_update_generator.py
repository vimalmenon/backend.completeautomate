from backend.data import YouTubeVideoDBData, YouTubeVideoStatsUpdateJobData
from backend.database import YouTubeVideoDB
from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration import YouTubeAPI


class YouTubeVideoStatsUpdate(BaseGenerator):
    def __init__(self, job):
        super().__init__(job)
        self.task_data = YouTubeVideoStatsUpdateJobData.to_cls(job.task_data)
        self.youtube_db = YouTubeVideoDB(ref_id=self.task_data.ref_id)
        self.youtube_api = YouTubeAPI()
        self.channel_id = self.task_data.platform.channel_id

    def generate(self) -> tuple[JobsStatusEnum, dict]:
        videos = self.youtube_db.fetch_videos_by_channel(secondary=self.channel_id)
        for video in videos:
            if video.past_update_time(days=3):
                api_response = self.youtube_api.fetch_video_details(
                    video_id=video.platform.video_id
                )
                new_video = YouTubeVideoDBData.to_cls_from_response(api_response)
                values = video.values_to_update(new_video)
                self.youtube_db.update_values(values=values)
                return JobsStatusEnum.IN_PROGRESS, self.task_data.to_json()
        return JobsStatusEnum.IN_PROGRESS, self.task_data.to_json()
