from backend.data import YouTubeVideoDBData
from backend.database import YouTubeVideoDB


class YouTubeVideoManager:

    def __init__(self, channel_id: str):
        self.channel_id = channel_id

    def get_video_by_id(self, video_id: str) -> YouTubeVideoDBData | None:
        return YouTubeVideoDB(channel_id=self.channel_id).fetch_video_from_db(video_id)

    def get_all_videos(self) -> list[YouTubeVideoDBData]:
        return YouTubeVideoDB(channel_id=self.channel_id).get_all_videos_from_db()

    def save_data(self, data: YouTubeVideoDBData) -> None:
        return YouTubeVideoDB(channel_id=self.channel_id).add_video(data)

    def update_summarized_transcript(
        self, video_id: str, summarized_transcript: str
    ) -> None:
        YouTubeVideoDB(channel_id=self.channel_id).update_transcript(
            video_id, summarized_transcript
        )

    def update_metadata(
        self, video_id: str, title: str, description: str, tags: list[str]
    ):
        # TODO Need to implement
        pass

    def update_transcript(self):
        # TODO Need to implement
        pass
