import logging

from backend.data import JobDataResponse
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class PromptSuggesterJob(BaseJob):
    types = [
        JobTypeEnum.PromptImprover,
    ]

    def execute(self) -> JobDataResponse:
        try:
            return JobDataResponse(status=JobsStatusEnum.IN_PROGRESS)
        except Exception:
            return JobDataResponse(status=JobsStatusEnum.FAILED)
