from backend.data import PromptDBData
from backend.database import PromptDB
from backend.enum import PromptTaskEnum


class PromptManager:

    def get_prompt_by_task(self, task: PromptTaskEnum) -> PromptDBData | None:
        return PromptDB().get_prompt_by_task(task)

    def get_prompts(self) -> list[PromptDBData]:
        return PromptDB().get_all_prompts()

    def add_prompt(self, data: PromptDBData) -> None:
        return PromptDB().save_prompt(data=data)

    def delete_prompt(self, prompt_task: PromptTaskEnum) -> None:
        return PromptDB().delete_prompt(prompt_task=prompt_task)
