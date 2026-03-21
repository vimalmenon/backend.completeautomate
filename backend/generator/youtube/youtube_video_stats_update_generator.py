from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator


class YouTubeVideoStatsUpdate(BaseGenerator):

    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
        return JobsStatusEnum.IN_PROGRESS, None
