import logging

from boto3.dynamodb.conditions import Attr, Key

from backend.data import ImagePromptDBData
from backend.database import DbManager
from backend.enum import DbKeysEnum

logger = logging.getLogger(__name__)


class ImagePromptDB:
    TABLE = "CA#IMAGE_PROMPT"

    def __init__(self):
        self.db_manager = DbManager()

    def save_to_db(self, data: ImagePromptDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(data.id),
                **data.to_json(),
            }
        )

    def get_by_task_id(self, task_id: str) -> list[ImagePromptDBData]:
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
            filter_expression=Attr("task_id").eq(task_id),
        )
        return [ImagePromptDBData.to_cls(item) for item in items]

    def update_data(self, data: ImagePromptDBData) -> None:
        # TODO Need to implement
        pass
