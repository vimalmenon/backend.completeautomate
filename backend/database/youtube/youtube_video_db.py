from logging import getLogger

from boto3.dynamodb.conditions import Key

from backend.data import YouTubeTranscriptDBData, YouTubeVideoDBData
from backend.data.platform import PlatformYouTubeVideoDBData
from backend.database import DbManager
from backend.enum import DbKeysEnum

logger = getLogger(__name__)


class YouTubeVideoDB:
    TABLE = "CA#YOUTUBE_VIDEO"

    def __init__(self, channel_id: str):
        self.db_manager = DbManager()
        self.channel_id = channel_id

    def fetch_video_from_db(self, video_id: str) -> YouTubeVideoDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{self.channel_id}#{video_id}",
            }
        )
        if item:
            return YouTubeVideoDBData.to_cls(item)
        return None

    def delete_video(self, video_id: str) -> None:
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{self.channel_id}#{video_id}",
            }
        )
        logger.info(f"Deleted video with id: {video_id}")

    def get_all_videos_from_db(self) -> list[YouTubeVideoDBData]:
        results = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE)
        )
        return [YouTubeVideoDBData.to_cls(result) for result in results]

    def add_video(self, video: YouTubeVideoDBData) -> None:
        video_data = video.platform.data
        if not isinstance(video_data, PlatformYouTubeVideoDBData):
            raise ValueError("Expected PlatformYouTubeVideoDBData")
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{video_data.channel_id}#{video_data.video_id}",
                **video.to_json(),
            }
        )

    def update_video(self, channel: dict) -> None:
        update_expression = []
        expression_attribute_values = {}
        for item, value in channel.items():
            update_expression.append(f"{item} = :{item}")
            expression_attribute_values[f":{item}"] = value
            logger.info(f"Updating {item} from {value}")
        self.db_manager.update_item(
            Key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{self.channel_id}#{self.channel_id}",
            },
            UpdateExpression=f"SET {', '.join(update_expression)}",
            ExpressionAttributeValues=expression_attribute_values,
        )

    def update_transcript(
        self, video_id: str, transcript: YouTubeTranscriptDBData
    ) -> None:
        self.db_manager.update_item(
            Key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{self.channel_id}#{video_id}",
            },
            UpdateExpression="SET transcript = :transcript",
            ExpressionAttributeValues={":transcript": transcript.to_json()},
        )
        logger.info(f"Updated transcript for video id: {video_id}")

    def update_video_details(self, video_id: str, title: str, description: str) -> None:
        self.db_manager.update_item(
            Key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{self.channel_id}#{video_id}",
            },
            UpdateExpression="SET title = :title, description = :description",
            ExpressionAttributeValues={
                ":title": title,
                ":description": description,
            },
        )
        logger.info(f"Updated video details for video id: {video_id}")
