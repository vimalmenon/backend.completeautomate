from backend.data import TaskData
from backend.enum.status import TaskStatusEnum
from backend.generator.image_prompt_generator import ImagePromptGenerator
from backend.jobs.base_job import BaseJob


class ImagePromptJob(BaseJob):

    def execute(self, task: TaskData) -> tuple[TaskStatusEnum, int]:
        try:
            return (ImagePromptGenerator(task).generate(), 0)
        except Exception:
            return (TaskStatusEnum.FAILED, task.failed_count + 1)
