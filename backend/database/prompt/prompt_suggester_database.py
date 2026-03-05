from boto3.dynamodb.conditions import Key

from backend.data import PromptSuggesterDBData
from backend.database.dynamo_database import DbManager
from backend.enum import DbKeysEnum


class PromptSuggesterDB:
    TABLE = "CA#PROMPT_SUGGESTER"

    def __init__(self):
        self.db_manager = DbManager()

    def get_prompts(self) -> list[PromptSuggesterDBData]:
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE)
        )
        return [PromptSuggesterDBData.to_cls(item) for item in items]

    def add_prompt(self, data: PromptSuggesterDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: data.task.value,
                **data.to_json(),
            }
        )
