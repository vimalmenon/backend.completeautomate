from backend.data import TaskData, YouTubeVideoDetailJobData
from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration.youtube.youtube_api import YouTubeAPI


class YouTubeVideoMetadataUpdater(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)
        self.job_data = YouTubeVideoDetailJobData.to_cls(task.payload)
        self.youtube_api = YouTubeAPI()

    def generate(self) -> TaskStatusEnum:
        self.youtube_api.update_video_metadata(
            video_id=self.job_data.platform.video_id,
            title=self.job_data.title,
            description=self.job_data.description,
            tags=self.job_data.tags,
        )
        return TaskStatusEnum.COMPLETED
