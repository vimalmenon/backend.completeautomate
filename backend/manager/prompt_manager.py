from datetime import datetime

from backend.data import PromptDBData
from backend.data.api import PromptUpdateResult
from backend.database import PromptDB
from backend.enum import AIModelEnum, PromptTaskEnum
from backend.exception import AppException


class PromptManager:

    def get_prompt_by_task(self, task: PromptTaskEnum) -> PromptDBData | None:
        return PromptDB().get_prompt_by_task(task)

    def get_prompts(self) -> list[PromptDBData]:
        return PromptDB().get_all_prompts()

    def add_prompt(self, data: PromptDBData) -> None:
        return PromptDB().save_prompt(data=data)

    def update_prompt(
        self, task: PromptTaskEnum, data: PromptUpdateResult
    ) -> PromptDBData:
        prompt = self.get_prompt_by_task(task=task)
        if prompt is None:
            raise AppException(f"Prompt not found for task {task.value}")

        updated_prompt = prompt.with_updated_prompt_version(
            prompt=data.prompt,
            system_message=data.system_message,
            description=data.description,
            ai=AIModelEnum(data.ai),
            created_at=datetime.now(),
            version=data.version,
            comment=data.comment,
        )
        PromptDB().update_prompt(prompt_task=task, values=updated_prompt.to_json())
        return updated_prompt

    def delete_prompt(self, prompt_task: PromptTaskEnum) -> None:
        return PromptDB().delete_prompt(prompt_task=prompt_task)
