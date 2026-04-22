from unittest.mock import MagicMock, patch

import pytest

from backend.exception import AppException
from backend.integration.youtube.youtube_api import YouTubeAPI


@pytest.mark.unit
class TestYouTubeAPI:

    @patch("backend.integration.youtube.youtube_api.YouTubeAuth")
    def test_update_video_metadata_success(self, mock_youtube_auth: MagicMock) -> None:
        mock_youtube = MagicMock()
        mock_videos_resource = MagicMock()

        mock_youtube_auth.return_value.get_authenticated_service.return_value = (
            mock_youtube
        )
        mock_youtube.videos.return_value = mock_videos_resource

        mock_videos_resource.list.return_value.execute.return_value = {
            "items": [
                {
                    "snippet": {
                        "title": "Old title",
                        "description": "Old description",
                        "tags": ["old"],
                        "categoryId": "22",
                    }
                }
            ]
        }
        mock_videos_resource.update.return_value.execute.return_value = {"id": "vid-1"}

        api = YouTubeAPI()
        result = api.update_video_metadata(
            video_id="vid-1",
            title="New title",
            description="New description",
            tags=["python", "automation"],
        )

        assert result is True
        mock_videos_resource.update.assert_called_once_with(
            part="snippet",
            body={
                "id": "vid-1",
                "snippet": {
                    "categoryId": "22",
                    "title": "New title",
                    "description": "New description",
                    "tags": ["python", "automation"],
                },
            },
        )

    @patch("backend.integration.youtube.youtube_api.YouTubeAuth")
    def test_update_video_metadata_requires_fields(
        self, mock_youtube_auth: MagicMock
    ) -> None:
        api = YouTubeAPI()

        with pytest.raises(
            AppException,
            match="At least one field must be provided",
        ):
            api.update_video_metadata(video_id="vid-1")

        mock_youtube_auth.return_value.get_authenticated_service.assert_not_called()

    @patch("backend.integration.youtube.youtube_api.YouTubeAuth")
    def test_update_video_metadata_raises_when_video_not_found(
        self, mock_youtube_auth: MagicMock
    ) -> None:
        mock_youtube = MagicMock()
        mock_videos_resource = MagicMock()

        mock_youtube_auth.return_value.get_authenticated_service.return_value = (
            mock_youtube
        )
        mock_youtube.videos.return_value = mock_videos_resource
        mock_videos_resource.list.return_value.execute.return_value = {"items": []}

        api = YouTubeAPI()

        with pytest.raises(AppException, match="not found"):
            api.update_video_metadata(video_id="missing", title="New title")
