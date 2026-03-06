import logging

from backend.data import YouTubeVideoThumbnailPromptSuggesterJobData
from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class YoutubeVideoThumbnailImagePromptSuggester(BaseGenerator):

    def __init__(self, task):
        super().__init__(task)
        self.job_data = YouTubeVideoThumbnailPromptSuggesterJobData.to_cls(
            {**task.payload, "task_id": task.id}
        )

    def generate(self) -> TaskStatusEnum:
        return TaskStatusEnum.IN_PROGRESS
