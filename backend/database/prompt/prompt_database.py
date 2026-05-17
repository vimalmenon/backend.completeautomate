from uuid import UUID

from boto3.dynamodb.conditions import Key

from backend.data import PromptDBData, PromptVersionDBData
from backend.database.dynamo_database import DbManager
from backend.enum import DbKeysEnum, PromptTaskEnum


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

    def update_prompt(self, prompt_task: PromptTaskEnum, values: dict) -> None:
        self.db_manager.update_data(
            key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: prompt_task.value,
            },
            values=values,
        )

    def delete_prompt(self, prompt_task: PromptTaskEnum) -> None:
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: prompt_task.value,
            }
        )


class PromptVersionDB:
    TABLE = "CA#PROMPT_VERSION"

    def __init__(self):
        self.db_manager = DbManager()

    def save_version(self, data: PromptVersionDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{data.task.value}#{data.version}",
                **data.to_json(),
            }
        )

    def get_version(
        self, prompt_task: PromptTaskEnum, version_id: UUID
    ) -> PromptVersionDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{prompt_task.value}#{version_id}",
            }
        )
        if item:
            return PromptVersionDBData.to_cls(item)
        return None

    def get_version_history(
        self, prompt_task: PromptTaskEnum
    ) -> list[PromptVersionDBData]:
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
            filter_expression=None,
        )
        return [
            PromptVersionDBData.to_cls(item)
            for item in items
            if item.get("task") == prompt_task.value
        ]

    def delete_version(self, prompt_task: PromptTaskEnum, version_id: UUID) -> None:
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{prompt_task.value}#{version_id}",
            }
        )
