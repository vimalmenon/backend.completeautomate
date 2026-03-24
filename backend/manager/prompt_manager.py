from backend.data import PromptDBData
from backend.database import PromptDB


class PromptManager:

    def get_prompts(self) -> list[PromptDBData]:
        return PromptDB().get_all_prompts()

    def add_prompt(self, data: PromptDBData) -> None:
        return PromptDB().save_prompt(data=data)
