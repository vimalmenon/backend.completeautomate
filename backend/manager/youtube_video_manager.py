from backend.data import ImagePromptData, YouTubeVideoDBData, YouTubeVideoMetadataData
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

    def update_metadata(self, title: str, description: str, tags: list[str]) -> None:
        YouTubeVideoDB(ref_id=self.ref_id).update_video_details(
            title=title, description=description, tags=tags
        )

    def update_transcript(self, transcript: str) -> None:
        YouTubeVideoDB(ref_id=self.ref_id).update_transcript(transcript)

    def update_summarized_transcript(self, summarized_transcript: str) -> None:
        YouTubeVideoDB(ref_id=self.ref_id).update_summarized_transcript(
            summarized_transcript
        )

    def update_metadata_suggestions(
        self, metadata_suggestions: list[YouTubeVideoMetadataData]
    ):
        data = [suggestion.to_json() for suggestion in metadata_suggestions]
        YouTubeVideoDB(ref_id=self.ref_id).update_metadata_suggestions(
            metadata_suggestions=data
        )

    def update_thumbnail_prompt_suggestions(
        self, thumbnail_prompt_suggestions: list[ImagePromptData]
    ):
        data = [suggestion.to_json() for suggestion in thumbnail_prompt_suggestions]
        YouTubeVideoDB(ref_id=self.ref_id).update_thumbnail_prompt_suggestions(
            thumbnail_prompt_suggestions=data
        )

    def update_video(self, values: dict) -> None:
        YouTubeVideoDB(ref_id=self.ref_id).update_video(values=values)
