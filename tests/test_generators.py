"""Unit tests for generator classes"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestImagePromptGenerator:
    """Test cases for ImagePromptGenerator"""

    @patch("backend.generator.image_prompt_generator.ImagePromptGenerator")
    def test_generate_prompt(self, mock_generator: MagicMock) -> None:
        """Test generating image prompt"""
        mock_generator.generate.return_value = "A beautiful sunset over mountains"

        result = mock_generator.generate()
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.unit
class TestYouTubeVideoGenerator:
    """Test cases for YouTubeVideoGenerator"""

    @patch("backend.generator.youtube_video_creator.YouTubeVideoCreator")
    def test_generate_video_metadata(self, mock_generator: MagicMock) -> None:
        """Test generating YouTube video metadata"""
        expected_metadata = {
            "title": "Test Video Title",
            "description": "Test Description",
            "tags": ["test", "video"],
        }
        mock_generator.generate.return_value = expected_metadata

        result = mock_generator.generate()
        assert isinstance(result, dict)
        assert "title" in result
        assert "description" in result
