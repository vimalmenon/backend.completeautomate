from backend.data import YouTubeVideoReviewerJobData
from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator


class YouTubeVideoReviewer(BaseGenerator):
    def __init__(self, task):
        super().__init__(task)
        self.job_data = YouTubeVideoReviewerJobData.to_cls(task.payload)

    def generate(self) -> TaskStatusEnum:
        return TaskStatusEnum.IN_PROGRESS
