from boto3.dynamodb.conditions import Key

from backend.data import YouTubeVideoMetadataDBData
from backend.database import DbManager
from backend.enum import DbKeysEnum, JobStatusEnum


class YouTubeVideoMetadataSuggesterDB:
    TABLE = "CA#YOUTUBE_VIDEO_METADATA_SUGGESTER"

    def __init__(self, ref_id: str):
        self.db_manager = DbManager()
        self.ref_id = ref_id

    def add_data(self, data: YouTubeVideoMetadataDBData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: data.ref_id,
                **data.to_json(),
            }
        )

    def fetch_suggestion(self) -> YouTubeVideoMetadataDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
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

    def update_option_status(
        self,
        option_index: int,
        status: JobStatusEnum,
    ) -> bool:
        suggestion = self.fetch_suggestion()
        if not suggestion:
            return False

        if option_index < 0 or option_index >= len(suggestion.video_details):
            return False

        suggestion.video_details[option_index].status = status
        self.db_manager.update_data(
            key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: self.ref_id,
            },
            values={
                "video_details": [
                    detail.to_json() for detail in suggestion.video_details
                ]
            },
        )
        return True
