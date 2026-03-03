from backend.data import PlatformDBData
from backend.database.dynamo_database import DbManager
from backend.enum import DbKeysEnum
from backend.exception.app_exception import AppException


class PlatformDB:
    TABLE = "CA#PLATFORM"

    def __init__(self):
        self.db_manager = DbManager()

    def get_data(self, ref_id: str) -> PlatformDBData:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: ref_id,
            }
        )
        if item:
            return PlatformDBData.to_cls(item)
        raise AppException(f"data with reference : {ref_id} not found")

    def save_data(self, data: PlatformDBData) -> str:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{data.platform_type.value}#{data.data.channel_id}",
                **data.to_json(),
            }
        )
        return ""
