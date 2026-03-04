from backend.data import PromptSuggesterDBData
from backend.database.dynamo_database import DbManager


class PromptSuggesterDB:
    TABLE = "CA#PROMPT_SUGGESTER"

    def __init__(self):
        self.db_manager = DbManager()

    def get_prompts(self) -> list[PromptSuggesterDBData]:
        # TODO Need implementation
        return []

    def add_prompt(self, data: PromptSuggesterDBData):
        # TODO Need implementation
        pass
