from boto3.dynamodb.conditions import Key

from backend.data import PromptDBData
from backend.database.dynamo_database import DbManager
from backend.enum import PromptTaskEnum
from backend.enum.db_keys import DbKeysEnum


class PromptDB:
    TABLE = "CA#PROMPT"

    def __init__(self):
        self.db_manager = DbManager()

    def save_prompt(self, data: PromptDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: data.task.value,
                **data.to_json(),
            }
        )

    def get_prompt_by_task(self, prompt_task: PromptTaskEnum) -> PromptDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: prompt_task.value,
            }
        )
        if item:
            return PromptDBData.to_cls(item)
        return None

    def get_all_prompts(self) -> list[PromptDBData]:
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE)
        )
        return [PromptDBData.to_cls(item) for item in items]
