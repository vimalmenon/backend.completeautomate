from backend.data import YouTubeVideoDBData
from backend.database import YouTubeVideoDB


class YouTubeVideoManager:

    def get_video_by_id(
        self, channel_id: str, video_id: str
    ) -> YouTubeVideoDBData | None:
        return YouTubeVideoDB(channel_id).fetch_video_from_db(video_id)

    def get_all_videos(self, channel_id: str) -> list[YouTubeVideoDBData]:
        return YouTubeVideoDB(channel_id).get_all_videos_from_db()
