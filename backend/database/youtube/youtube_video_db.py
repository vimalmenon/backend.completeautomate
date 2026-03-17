from logging import getLogger

from boto3.dynamodb.conditions import Key

from backend.data import YouTubeVideoDBData
from backend.database import DbManager
from backend.enum import DbKeysEnum

logger = getLogger(__name__)


class YouTubeVideoDB:
    TABLE = "CA#YOUTUBE_VIDEO"

    def __init__(self, ref_id: str):
        self.db_manager = DbManager()
        self.ref_id = ref_id

    def fetch_video_from_db(self) -> YouTubeVideoDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
            }
        )
        if item:
            return YouTubeVideoDBData.to_cls(item)
        return None

    def delete_video(self, video_id: str) -> None:
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
            }
        )
        logger.info(f"Deleted video with id: {video_id}")

    def get_all_videos_from_db(self) -> list[YouTubeVideoDBData]:
        results = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE)
        )
        return [YouTubeVideoDBData.to_cls(result) for result in results]

    def add_video(self, video: YouTubeVideoDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
                **video.to_json(),
            }
        )

    def update_values(self, values: dict) -> None:
        self.db_manager.update_data(
            key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
            },
            values=values,
        )
