import logging

from backend.data import JobDataResponse
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import PromptReviewer
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class PromptSuggesterJob(BaseJob):
    types = [
        JobTypeEnum.PromptImprover,
    ]

    def execute(self) -> JobDataResponse:
        try:
            status, task_data = PromptReviewer(job=self.job).generate()
            return JobDataResponse(status=status, task_data=task_data)
        except Exception:
            return JobDataResponse(status=JobsStatusEnum.FAILED)
