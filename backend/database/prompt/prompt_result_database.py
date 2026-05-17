from uuid import UUID

from boto3.dynamodb.conditions import Key

from backend.data import PromptResultDBData
from backend.database.dynamo_database import DbManager
from backend.enum import DbKeysEnum, PromptTaskEnum


class PromptResultDB:
    TABLE = "CA#PROMPT_RESULT"

    def __init__(self):
        self.db_manager = DbManager()

    def save_result(self, data: PromptResultDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{data.task.value}#{data.result_id}",
                **data.to_json(),
            }
        )

    def get_results_by_task(
        self, prompt_task: PromptTaskEnum
    ) -> list[PromptResultDBData]:
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
        )
        return [
            PromptResultDBData.to_cls(item)
            for item in items
            if item.get("task") == prompt_task.value
        ]

    def get_result(
        self, prompt_task: PromptTaskEnum, result_id: UUID
    ) -> PromptResultDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{prompt_task.value}#{result_id}",
            }
        )
        if item:
            return PromptResultDBData.to_cls(item)
        return None

    def delete_result(self, prompt_task: PromptTaskEnum, result_id: UUID) -> None:
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{prompt_task.value}#{result_id}",
            }
        )
