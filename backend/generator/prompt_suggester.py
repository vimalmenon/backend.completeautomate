from backend.data import (
    TaskData,
)
from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator


class PromptSuggester(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)

    def generate(self) -> JobsStatusEnum:
        # TODO Need to implement
        return JobsStatusEnum.IN_PROGRESS
