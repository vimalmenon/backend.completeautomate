import logging

from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class PromptSuggesterJob(BaseJob):
    types = [
        JobTypeEnum.PromptImprover,
    ]

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        try:
            return JobsStatusEnum.IN_PROGRESS, 1, None
        except Exception:
            return (JobsStatusEnum.FAILED, 0, None)
