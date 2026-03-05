from boto3.dynamodb.conditions import Key

from backend.data import YouTubeVideoMetadataDBData
from backend.database import DbManager
from backend.enum import DbKeysEnum


class YouTubeVideoMetadataSuggesterDB:
    TABLE = "CA#YOUTUBE_VIDEO_METADATA_SUGGESTER"

    def __init__(self):
        self.db_manager = DbManager()

    def add_data(self, data: YouTubeVideoMetadataDBData) -> None:
        channel_id = data.platform.channel_id
        video_id = data.platform.video_id
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{channel_id}#{video_id}",
                **data.to_json(),
            }
        )

    def fetch_suggestion(
        self, channel_id: str, video_id: str
    ) -> YouTubeVideoMetadataDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{channel_id}#{video_id}",
            }
        )
        if item:
            return YouTubeVideoMetadataDBData.to_cls(item)
        return None

    def get_all_suggestions(self) -> list[YouTubeVideoMetadataDBData]:
        results = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE)
        )
        return [YouTubeVideoMetadataDBData.to_cls(result) for result in results]
