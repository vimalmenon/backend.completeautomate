import logging
import traceback

from backend.enum import JobStatusEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class PromptSuggesterJob(BaseJob):

    def execute(self) -> tuple[JobStatusEnum, int]:
        try:
            pass
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                "Error executing PromptSuggester task %s: %s", self.task.id, error_msg
            )
            return (JobStatusEnum.FAILED, self.task.failed_count + 1)
