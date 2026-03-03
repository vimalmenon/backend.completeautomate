import logging

from backend.data import TaskData
from backend.enum.status import TaskStatusEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class NoJob(BaseJob):

    def execute(self, task: TaskData) -> tuple[TaskStatusEnum, int]:
        logger.error(
            "No job handler available for task %s",
            task.id,
        )
        return (TaskStatusEnum.FAILED, task.failed_count + 1)
