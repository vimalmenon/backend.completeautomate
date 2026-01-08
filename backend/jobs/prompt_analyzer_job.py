from backend.data import Task
from backend.enum import TaskStatusEnum
from backend.jobs.base_job import BaseJob


class PromptAnalyzerJob(BaseJob):

    def execute(self, task: Task) -> tuple[TaskStatusEnum, int]:
        return TaskStatusEnum.IN_PROGRESS, 0
