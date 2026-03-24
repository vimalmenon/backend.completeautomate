from typing import Any

from backend.factory.youtube_api_factory import youtube_channel_api_factory


class MockYouTubeAPI:
    """Drop-in mock for YouTubeAPI, returned when OFFLINE mode is enabled.

    All read methods return realistic stub dicts matching the live API shape.
    All write methods are no-ops that return True.
    """

    def update_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        return True

    def update_video_metadata(
        self,
        video_id: str,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        return True

    def get_channel_info(self, channel_id: str) -> dict[str, Any]:
        return youtube_channel_api_factory()

    def create_text_post(
        self, channel_id: str, text: str, video_id: str | None = None
    ) -> bool:
        return True

    def create_video_comment(self, channel_id: str, video_id: str, text: str) -> bool:
        return True

    def list_all_videos(
        self, channel_id: str, max_results: int = 50
    ) -> list[dict[str, Any]]:
        return [self._mock_video_item(f"mock_video_{i}") for i in range(1, 4)]

    def fetch_video_details(self, video_id: str) -> dict[str, Any]:
        return self._mock_video_item(video_id)

    def get_transcript(self, video_id: str) -> str:
        return (
            "This is a mock transcript generated for offline mode. "
            "It provides sample content so the full generator pipeline "
            "can be exercised without a live YouTube connection."
        )

    def _mock_video_item(self, video_id: str) -> dict[str, Any]:
        return {
            "id": video_id,
            "snippet": {
                "title": f"Mock Video Title [{video_id}]",
                "description": "Mock video description for offline mode.",
                "publishedAt": "2024-03-01T12:00:00Z",
                "thumbnails": {
                    "high": {"url": "https://example.com/mock_thumbnail.jpg"}
                },
                "tags": ["mock", "offline", "test"],
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en",
            },
            "statistics": {
                "viewCount": "1000",
                "likeCount": "50",
                "commentCount": "10",
            },
            "status": {"privacyStatus": "public"},
        }
