from functools import lru_cache
from typing import Any

from boto3.dynamodb.conditions import Key

from backend.data import (
    PlatformDBData,
)
from backend.database.dynamo_database import DbManager
from backend.enum import DbKeysEnum
from backend.exception import AppException


class PlatformDB:
    TABLE = "CA#PLATFORM"

    def __init__(self):
        self.db_manager = DbManager()

    @classmethod
    @lru_cache(maxsize=256)
    def _get_item_cached(cls, ref_id: str) -> Any | None:
        return DbManager().get_item(
            {
                DbKeysEnum.Primary.value: cls.TABLE,
                DbKeysEnum.Secondary.value: ref_id,
            }
        )

    def get_data(self, ref_id: str) -> PlatformDBData:
        item = self._get_item_cached(ref_id)
        if item:
            return PlatformDBData.to_cls(item)
        raise AppException(f"data with reference : {ref_id} not found")

    def save_data(self, data: PlatformDBData) -> str:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: data.ref_id,
                **data.to_json(),
            }
        )
        self._get_item_cached.cache_clear()
        return data.ref_id

    def get_platforms(self) -> list[PlatformDBData]:
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE)
        )
        return [PlatformDBData.to_cls(item) for item in items]
