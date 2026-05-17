from datetime import datetime
from uuid import uuid4

from backend.data import PromptDBData, PromptResultDBData, PromptVersionDBData
from backend.data.api import PromptUpdateResult
from backend.database import PromptDB, PromptResultDB, PromptVersionDB
from backend.enum import AIModelEnum, PromptTaskEnum
from backend.exception import AppException


class PromptManager:

    def get_prompt_by_task(self, task: PromptTaskEnum) -> PromptDBData | None:
        return PromptDB().get_prompt_by_task(task)

    def get_prompts(self) -> list[PromptDBData]:
        return PromptDB().get_all_prompts()

    def add_prompt(self, data: PromptDBData | PromptUpdateResult) -> PromptDBData:
        if isinstance(data, PromptDBData):
            PromptDB().save_prompt(data)
            version = PromptVersionDBData(
                task=data.task,
                version=data.active_version,
                prompt=data.prompt,
                system_message=data.system_message,
                reflect_message="",
                ai=data.ai,
                created_at=data.last_updated,
                examples=data.examples,
            )
            PromptVersionDB().save_version(data=version)
            return data

        task = PromptTaskEnum(data.task)
        existing_prompt = self.get_prompt_by_task(task=task)
        if existing_prompt is not None:
            raise AppException(f"Prompt already exists for task {task.value}")

        version_id = data.version or uuid4()
        created_at = datetime.now()
        examples = data.examples or []

        prompt = PromptDBData(
            task=task,
            description=data.description,
            active_version=version_id,
            prompt=data.prompt,
            system_message=data.system_message,
            ai=AIModelEnum(data.ai),
            comment=data.comment,
            last_updated=created_at,
            examples=examples,
        )

        version = PromptVersionDBData(
            task=task,
            version=version_id,
            prompt=data.prompt,
            system_message=data.system_message,
            reflect_message="",
            ai=AIModelEnum(data.ai),
            created_at=created_at,
            examples=examples,
        )

        PromptDB().save_prompt(data=prompt)
        PromptVersionDB().save_version(data=version)
        return prompt

    def update_prompt(
        self, task: PromptTaskEnum, data: PromptUpdateResult
    ) -> PromptDBData:
        existing = self.get_prompt_by_task(task=task)
        if existing is None:
            raise AppException(f"Prompt not found for task {task.value}")

        version_id = data.version or uuid4()
        created_at = datetime.now()
        examples = data.examples or existing.examples

        version = PromptVersionDBData(
            task=task,
            version=version_id,
            prompt=data.prompt,
            system_message=data.system_message,
            reflect_message="",
            ai=AIModelEnum(data.ai),
            created_at=created_at,
            examples=examples,
        )
        PromptVersionDB().save_version(data=version)

        updated_prompt = PromptDBData(
            task=task,
            description=data.description,
            active_version=version_id,
            prompt=data.prompt,
            system_message=data.system_message,
            ai=AIModelEnum(data.ai),
            comment=data.comment,
            last_updated=created_at,
            examples=examples,
        )
        PromptDB().update_prompt(prompt_task=task, values=updated_prompt.to_json())
        return updated_prompt

    def delete_prompt(self, prompt_task: PromptTaskEnum) -> None:
        PromptDB().delete_prompt(prompt_task=prompt_task)

    def get_version_history(self, task: PromptTaskEnum) -> list[PromptVersionDBData]:
        return PromptVersionDB().get_version_history(task)

    def add_result(self, data: PromptResultDBData) -> None:
        PromptResultDB().save_result(data)

    def get_results(self, task: PromptTaskEnum) -> list[PromptResultDBData]:
        return PromptResultDB().get_results_by_task(task)

    # ── Example Management ──

    def get_examples(self, task: PromptTaskEnum) -> list[dict]:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        return prompt.examples

    def add_example(self, task: PromptTaskEnum, example: dict) -> list[dict]:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        examples = prompt.examples + [example]
        PromptDB().update_prompt(
            prompt_task=task,
            values={"examples": examples},
        )
        return examples

    def remove_example(self, task: PromptTaskEnum, index: int) -> list[dict]:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        if index < 0 or index >= len(prompt.examples):
            raise AppException(
                f"Example index {index} out of range (0-{len(prompt.examples) - 1})"
            )
        examples = prompt.examples[:index] + prompt.examples[index + 1 :]
        PromptDB().update_prompt(
            prompt_task=task,
            values={"examples": examples},
        )
        return examples

    def clear_examples(self, task: PromptTaskEnum) -> None:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        PromptDB().update_prompt(
            prompt_task=task,
            values={"examples": []},
        )

    def set_examples(self, task: PromptTaskEnum, examples: list[dict]) -> list[dict]:
        prompt = self.get_prompt_by_task(task)
        if not prompt:
            raise AppException(f"Prompt not found for task {task.value}")
        PromptDB().update_prompt(
            prompt_task=task,
            values={"examples": examples},
        )
        return examples
