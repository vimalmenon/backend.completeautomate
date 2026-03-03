import logging

from backend.enum.status import TaskStatusEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class NoJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        logger.error(
            "No job handler available for task %s",
            self.task.id,
        )
        return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
