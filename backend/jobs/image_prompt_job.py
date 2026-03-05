import logging
import traceback

from backend.enum.status import TaskStatusEnum
from backend.generator.image_prompt_generator import ImagePromptGenerator
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class ImagePromptJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        try:
            return (ImagePromptGenerator(self.task).generate(), 0)
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                "Error executing ImagePromptGenerator task %s: %s",
                self.task.id,
                error_msg,
            )
            return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
