from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator


class PromptReviewer(BaseGenerator):
    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
        return JobsStatusEnum.IN_PROGRESS, None
