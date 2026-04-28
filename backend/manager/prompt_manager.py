from datetime import datetime
from uuid import uuid4

from backend.data import PromptDBData, PromptVersionDBData
from backend.data.api import PromptUpdateResult
from backend.database import PromptDB
from backend.enum import AIModelEnum, PromptTaskEnum
from backend.exception import AppException


class PromptManager:

    def get_prompt_by_task(self, task: PromptTaskEnum) -> PromptDBData | None:
        return PromptDB().get_prompt_by_task(task)

    def get_prompts(self) -> list[PromptDBData]:
        return PromptDB().get_all_prompts()

    def add_prompt(self, data: PromptUpdateResult) -> PromptDBData:
        task = PromptTaskEnum(data.task)
        existing_prompt = self.get_prompt_by_task(task=task)
        if existing_prompt is not None:
            raise AppException(f"Prompt already exists for task {task.value}")

        version_id = data.version or uuid4()
        created_at = datetime.now()
        prompt = PromptDBData(
            task=task,
            description=data.description,
            version=version_id,
            versions=[
                PromptVersionDBData(
                    prompt=data.prompt,
                    system_message=data.system_message,
                    reflect_message="",
                    version=version_id,
                    ai=AIModelEnum(data.ai),
                    created_at=created_at,
                )
            ],
            comment=data.comment,
            last_updated=created_at,
        )
        PromptDB().save_prompt(data=prompt)
        return prompt

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
