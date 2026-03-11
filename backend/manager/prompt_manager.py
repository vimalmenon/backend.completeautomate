from backend.data import PromptDBData
from backend.database import PromptDB


class PromptManager:

    def get_prompts(self) -> list[PromptDBData]:
        return PromptDB().get_all_prompts()
