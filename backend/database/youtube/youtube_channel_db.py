from logging import getLogger

from backend.data import YouTubeChannelDBData
from backend.database import DbManager
from backend.enum import DbKeysEnum

logger = getLogger(__name__)


class YouTubeChannelDB:
    TABLE = "CA#YOUTUBE_CHANNEL"

    def __init__(self, channel_id: str):
        self.db_manager = DbManager()
        self.channel_id = channel_id

    def add_channel(self, data: YouTubeChannelDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.channel_id,
                **data.to_json(),
            }
        )

    def query_channel(self) -> YouTubeChannelDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.channel_id,
            }
        )
        if item:
            return YouTubeChannelDBData.to_cls(item)
        return None

    def delete_channel(self) -> None:
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.channel_id,
            }
        )
        logger.info(f"Deleted channel with id: {self.channel_id}")

    def update_channel(self, channel: dict):
        update_expression = []
        expression_attribute_values = {}
        for item, value in channel.items():
            update_expression.append(f"{item} = :{item}")
            expression_attribute_values[f":{item}"] = value
            logger.info(f"Updating {item} from {value}")
        self.db_manager.update_item(
            Key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.channel_id,
            },
            UpdateExpression=f"SET {', '.join(update_expression)}",
            ExpressionAttributeValues=expression_attribute_values,
        )
