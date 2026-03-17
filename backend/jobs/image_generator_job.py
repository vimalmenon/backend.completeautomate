import logging
import traceback

from backend.enum import TaskStatusEnum
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class ImageGeneratorJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        try:
            logger.info("Executing ImageGeneratorJob for task %s", self.task.id)
            return (TaskStatusEnum.COMPLETED, 0)
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                "Error executing ImageGeneratorJob for task %s: %s",
                self.task.id,
                error_msg,
            )
            return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
