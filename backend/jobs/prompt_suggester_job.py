import logging
import traceback

from backend.enum import TaskStatusEnum
from backend.generator import PromptSuggester
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class PromptSuggesterJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        try:
            return PromptSuggester(self.task).generate(), 0
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                "Error executing PromptSuggester task %s: %s", self.task.id, error_msg
            )
            return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
