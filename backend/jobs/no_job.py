import logging

from backend.data import Task
from backend.enum.job import JobEnum
from backend.enum.status import TaskStatusEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class NoJob(BaseJob):
    job: JobEnum = JobEnum.DUMMY

    def execute(self, task: Task) -> tuple[TaskStatusEnum, int]:
        logger.error(
            "No job handler available for task %s with job type %s",
            task.id,
        )
        return (TaskStatusEnum.FAILED, task.failed_count + 1)
