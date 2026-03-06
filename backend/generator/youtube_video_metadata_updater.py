from backend.data import TaskData, YouTubeVideoMetadataJobData
from backend.enum import JobEnum, TaskStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration.youtube.youtube_api import YouTubeAPI
from backend.manager import TaskManager


class YouTubeVideoMetadataUpdater(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)
        self.job_data = YouTubeVideoMetadataJobData.to_cls(task.payload)
        self.youtube_api = YouTubeAPI()

    def generate(self) -> TaskStatusEnum:
        self.youtube_api.update_video_metadata(
            video_id=self.job_data.platform.video_id,
            title=self.job_data.title,
            description=self.job_data.description,
            tags=self.job_data.tags,
        )
        task_manager = TaskManager(self.task)
        next_task = task_manager.create_youtube_summarize_task(
            ref_id=self.job_data.ref_id,
            created_by=JobEnum.YouTubeVideoMetadataUpdater,
        )
        task_manager.add_task(next_task)
        return TaskStatusEnum.COMPLETED
