from backend.data import (
    Task,
)
from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator


class PromptAnalyzer(BaseGenerator):
    def __init__(self, task: Task):
        super().__init__(task)

    def generate(self) -> TaskStatusEnum:
        return TaskStatusEnum.IN_PROGRESS
