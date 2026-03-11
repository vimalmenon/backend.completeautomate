from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator


class YouTubeVideoReviewer(BaseGenerator):

    def generate(self) -> TaskStatusEnum:
        return TaskStatusEnum.IN_PROGRESS
