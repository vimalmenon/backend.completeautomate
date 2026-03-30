import logging

from backend.data import JobDataResponse
from backend.enum import JobsStatusEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class NoJob(BaseJob):

    def execute(self) -> JobDataResponse:
        logger.error(
            "No job handler available for task %s",
            self.job.id,
        )
        return JobDataResponse(status=JobsStatusEnum.FAILED)
