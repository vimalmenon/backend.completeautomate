from backend.data import YouTubeVideoDBData
from backend.database import YouTubeVideoDB


class YouTubeVideoManager:

    def __init__(self, ref_id: str):
        self.ref_id = ref_id

    def get_video(self) -> YouTubeVideoDBData | None:
        return YouTubeVideoDB(ref_id=self.ref_id).fetch_video_from_db()

    def get_all_videos(self) -> list[YouTubeVideoDBData]:
        return YouTubeVideoDB(ref_id=self.ref_id).get_all_videos_from_db()

    def save_data(self, data: YouTubeVideoDBData) -> None:
        return YouTubeVideoDB(ref_id=self.ref_id).add_video(data)

    def update_summarized_transcript(
        self, video_id: str, summarized_transcript: str
    ) -> None:
        YouTubeVideoDB(ref_id=self.ref_id).update_transcript(
            video_id, summarized_transcript
        )

    def update_metadata(
        self, video_id: str, title: str, description: str, tags: list[str]
    ) -> None:
        YouTubeVideoDB(ref_id=self.ref_id).update_video_details(
            video_id=video_id, title=title, description=description, tags=tags
        )

    def update_transcript(self, video_id: str, transcript: str) -> None:
        YouTubeVideoDB(ref_id=self.ref_id).update_transcript(video_id, transcript)

    # def update_summarized_transcript(
    #     self, video_id: str, summarized_transcript: str
    # ) -> None:
    #     YouTubeVideoDB(ref_id=self.ref_id).update_summarized_transcript(
    #         video_id, summarized_transcript
    #     )

    def update_video(self, values: dict) -> None:
        YouTubeVideoDB(ref_id=self.ref_id).update_video(values=values)
