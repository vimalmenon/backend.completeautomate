from backend.data import YouTubeThumbnailJobData
from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration.storage.s3_storage import S3Storage
from backend.integration.youtube.youtube_api import YouTubeAPI


class YouTubeThumbnailUpdater(BaseGenerator):

    def __init__(self, task):
        super().__init__(task)
        self.job_data = YouTubeThumbnailJobData.to_cls(self.task.payload)

    def generate(self) -> TaskStatusEnum:
        s3_data = self.job_data.data
        S3Storage().download_data(s3_data)
        YouTubeAPI().update_thumbnail(
            video_id=self.job_data.platform.video_id,
            thumbnail_path=s3_data.downloaded_path,
        )
        return TaskStatusEnum.COMPLETED
