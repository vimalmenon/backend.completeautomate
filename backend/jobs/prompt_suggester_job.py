from backend.enum import TaskStatusEnum
from backend.jobs.base_job import BaseJob


class PromptSuggesterJob(BaseJob):
    # TODO No implemention available

    def execute(self) -> tuple[TaskStatusEnum, int]:
        return TaskStatusEnum.IN_PROGRESS, 0
