import logging

from backend.enum.job import JobsStatusEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class NoJob(BaseJob):

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        logger.error(
            "No job handler available for task %s",
            self.task.id,
        )
        return (JobsStatusEnum.FAILED, self.task.failed_count + 1, None)
