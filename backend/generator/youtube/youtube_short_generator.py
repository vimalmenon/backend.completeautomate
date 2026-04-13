from backend.enum import (
    JobsStatusEnum,
)
from backend.generator.base_generator import BaseGenerator


class YouTubeShortGenerator(BaseGenerator):

    def generate(self) -> tuple[JobsStatusEnum, dict]:
        return (JobsStatusEnum.IN_PROGRESS, {})
