from backend.data import (
    TaskData,
)
from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator


class PromptSuggester(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)

    def generate(self) -> TaskStatusEnum:
        return TaskStatusEnum.IN_PROGRESS
