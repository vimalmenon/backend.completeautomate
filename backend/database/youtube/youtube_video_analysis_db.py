from backend.data import YouTubeVideoAnalysisDBData
from backend.database import DbManager
from backend.enum import DbKeysEnum


class YouTubeVideoAnalysisDB:
    TABLE = "CA#YOUTUBE_VIDEO_ANALYSIS"

    def __init__(self):
        self.db_manager = DbManager()

    def add_data(self, data: YouTubeVideoAnalysisDBData) -> None:
        channel_id = data.platform.channel_id
        video_id = data.platform.video_id
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: f"{channel_id}#{video_id}",
                **data.to_json(),
            }
        )
