from backend.enum import TaskStatusEnum
from backend.jobs.base_job import BaseJob


class TwitterJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        return TaskStatusEnum.IN_PROGRESS, 0
