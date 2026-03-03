from backend.enum.status import TaskStatusEnum
from backend.generator.image_generator import ImageGenerator
from backend.jobs.base_job import BaseJob


class ImageGeneratorJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        try:
            return (ImageGenerator(self.task).generate(), 0)
        except Exception:
            return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
