from backend.data import TaskData
from backend.enum import TaskStatusEnum
from backend.jobs.base_job import BaseJob


class PromptAnalyzerJob(BaseJob):

    def execute(self, task: TaskData) -> tuple[TaskStatusEnum, int]:
        return TaskStatusEnum.IN_PROGRESS, 0
