from logging import getLogger

from backend.data import YouTubeChannelDBData
from backend.database import DbManager
from backend.enum import DbKeysEnum

logger = getLogger(__name__)


class YouTubeChannelDB:
    TABLE = "CA#YOUTUBE_CHANNEL"

    def __init__(self, ref_id: str):
        self.db_manager = DbManager()
        self.ref_id = ref_id

    def add_channel(self, data: YouTubeChannelDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: data.ref_id,
                **data.to_json(),
            }
        )

    def query_channel(self) -> YouTubeChannelDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
            }
        )
        if item:
            return YouTubeChannelDBData.to_cls(item)
        return None

    def delete_channel(self) -> None:
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
            }
        )
        logger.info(f"Deleted channel with id: {self.ref_id}")

    def update_channel(self, channel: dict) -> None:
        self.db_manager.update_data(
            key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
            },
            values=channel,
        )

    def update_values(self, values: dict) -> None:
        self.db_manager.update_data(
            key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
            },
            values=values,
        )
