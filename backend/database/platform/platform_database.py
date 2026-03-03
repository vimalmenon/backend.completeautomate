from functools import lru_cache
from typing import Any

from backend.data import PlatformDBData
from backend.database.dynamo_database import DbManager
from backend.enum import DbKeysEnum, PlatformEnum
from backend.exception.app_exception import AppException


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
        secondary = None
        if data.platform_type == PlatformEnum.YouTubeVideo and hasattr(
            data.data, "video_id"
        ):
            secondary = f"{data.platform_type.value}#{data.data.channel_id}#{data.data.video_id}"
        if data.platform_type == PlatformEnum.YouTubeChannel:
            secondary = f"{data.platform_type.value}#{data.data.channel_id}"
        if not secondary:
            raise AppException(
                f"Platform with value : {data.platform_type.value} not found"
            )
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: secondary,
                **data.to_json(),
            }
        )
        self._get_item_cached.cache_clear()
        return secondary
