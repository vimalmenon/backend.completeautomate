from typing import Any

from backend.config.env import env
from backend.factory.common import fake_date, fake_url


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
        return [self._mock_video_item() for _i in range(1, 4)]

    def fetch_video_details(self, video_id: str) -> dict[str, Any]:
        return self._mock_video_item()

    def get_transcript(self, video_id: str) -> str:
        return (
            "This is a mock transcript generated for offline mode. "
            "It provides sample content so the full generator pipeline "
            "can be exercised without a live YouTube connection."
        )

    def _mock_video_item(self) -> dict[str, Any]:
        video_id = env.YOUTUBE_API_KEY
        return {
            "id": video_id,
            "snippet": {
                "title": f"Mock Video Title [{video_id}]",
                "description": "Mock video description for offline mode.",
                "publishedAt": "2024-03-01T12:00:00Z",
                "thumbnails": {"high": {"url": fake_url}},
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


def youtube_channel_api_factory(**kwargs) -> dict:
    video_id = env.YOUTUBE_API_KEY
    return {
        "id": video_id,
        "snippet": {
            "title": "Mock Channel",
            "description": "Mock channel description for offline mode.",
            "customUrl": "@mockchannel",
            "publishedAt": fake_date(),
            "thumbnails": {
                "high": {"url": "https://example.com/mock_channel_thumb.jpg"}
            },
        },
        "statistics": {
            "viewCount": "100000",
            "subscriberCount": "5000",
            "videoCount": "3",
        },
        "status": {"privacyStatus": "public"},
        "brandingSettings": {},
    }


def youtube_video_api_factory(**kwargs) -> dict:
    video_id = kwargs.get("video_id")
    return {
        "id": video_id,
        "snippet": {
            "title": f"Mock Video Title [{video_id}]",
            "description": "Mock video description for offline mode.",
            "publishedAt": fake_date,
            "thumbnails": {"high": {"url": "https://example.com/mock_thumbnail.jpg"}},
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


def youtube_video_transcript():
    return (
        "This is a mock transcript generated for offline mode. "
        "It provides sample content so the full generator pipeline "
        "can be exercised without a live YouTube connection."
    )
