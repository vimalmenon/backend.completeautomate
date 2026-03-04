from backend.enum import TaskStatusEnum
from backend.generator import PromptSuggester
from backend.jobs.base_job import BaseJob


class PromptSuggesterJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        try:
            return PromptSuggester(self.task).generate(), 0
        except Exception:
            return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
