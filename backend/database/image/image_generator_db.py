from boto3.dynamodb.conditions import Attr, Key

from backend.data import ImageGeneratorJobData
from backend.database import DbManager
from backend.enum import DbKeysEnum


class ImageGeneratorDB:
    TABLE = "CA#IMAGE"

    def __init__(self):
        self.db_manager = DbManager()

    def save_to_db(self, data: ImageGeneratorJobData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(data.id),
                **data.to_json(),
            }
        )

    def get_by_task_id(self, task_id: str) -> list[ImageGeneratorJobData]:
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
            filter_expression=Attr("task_id").eq(task_id),
        )
        return [ImageGeneratorJobData.to_cls(item) for item in items]
