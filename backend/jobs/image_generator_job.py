from backend.data import Task
from backend.enum.status import TaskStatusEnum
from backend.generator.image_generator import ImageGenerator
from backend.jobs.base_job import BaseJob


class ImageGeneratorJob(BaseJob):

    def execute(self, task: Task) -> tuple[TaskStatusEnum, int]:
        try:
            return (ImageGenerator(task).generate(), 0)
        except Exception:
            return (TaskStatusEnum.FAILED, task.failed_count + 1)
