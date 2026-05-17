"""Unit tests for data models"""

from uuid import uuid4

import pytest

from backend.data.image import ImagePromptJobData
from backend.data.prompt import PromptDBData
from backend.data.s3 import S3Data
from backend.data.youtube_channel import (
    YouTubeVideoThumbnailPromptSuggesterJobData,
)
from backend.enum import AIModelEnum, ImageTypeEnum
from backend.enum.prompt import PromptTaskEnum
from backend.enum.s3 import S3ContentTypeEnum


@pytest.mark.unit
class TestS3Data:
    """Test cases for S3Data model"""

    def test_create_s3_data(self) -> None:
        """Test creating S3Data instance"""
        s3_data = S3Data(
            name="test.png",
            content_type=S3ContentTypeEnum.PNG,
        )

        assert s3_data.name == "test.png"
        assert s3_data.content_type == S3ContentTypeEnum.PNG
        assert "images/test.png" in s3_data.s3_key

    def test_s3_data_downloaded_path(self) -> None:
        """Test downloaded path property"""
        s3_data = S3Data(
            name="test.png",
            content_type=S3ContentTypeEnum.PNG,
        )

        # The downloaded path should include the output directory
        assert "output" in str(s3_data.downloaded_path)
        assert "test.png" in str(s3_data.downloaded_path)

    def test_to_cls_from_path_with_key(self) -> None:
        """Test creating S3Data from path with key (category/key/name)"""
        s3_data = S3Data.to_cls_from_path("images/vacation/photo.png")

        assert s3_data.name == "photo.png"
        assert s3_data.key == "vacation"
        assert s3_data.content_type == S3ContentTypeEnum.PNG
        assert s3_data.s3_key == "images/vacation/photo.png"

    def test_to_cls_from_path_without_key(self) -> None:
        """Test creating S3Data from path without key (category/name)"""
        s3_data = S3Data.to_cls_from_path("images/photo.png")

        assert s3_data.name == "photo.png"
        assert s3_data.key is None
        assert s3_data.content_type == S3ContentTypeEnum.PNG
        assert s3_data.s3_key == "images/photo.png"

    def test_to_cls_from_path_json_with_key(self) -> None:
        """Test creating S3Data from JSON path with key"""
        s3_data = S3Data.to_cls_from_path("json/2024/data.json")

        assert s3_data.name == "data.json"
        assert s3_data.key == "2024"
        assert s3_data.content_type == S3ContentTypeEnum.JSON
        assert s3_data.s3_key == "json/2024/data.json"

    def test_to_cls_from_path_json_with_nested_key(self) -> None:
        """Test creating S3Data from JSON path with nested key"""
        s3_data = S3Data.to_cls_from_path("json/test/json/file.json")

        assert s3_data.name == "file.json"
        assert s3_data.key == "test/json"
        assert s3_data.content_type == S3ContentTypeEnum.JSON
        assert s3_data.s3_key == "json/test/json/file.json"

    def test_to_json_with_key(self) -> None:
        """Test JSON serialization includes key"""
        s3_data = S3Data(
            name="photo.png",
            content_type=S3ContentTypeEnum.PNG,
            key="vacation",
        )
        json_data = s3_data.to_json()

        assert json_data["name"] == "photo.png"
        assert json_data["key"] == "vacation"
        assert json_data["content_type"] == "image/png"

    def test_to_cls_json_deserialization_with_key(self) -> None:
        """Test JSON deserialization restores key"""
        data = {
            "name": "photo.png",
            "content_type": "image/png",
            "key": "vacation",
        }
        s3_data = S3Data.to_cls(data)

        assert s3_data.name == "photo.png"
        assert s3_data.key == "vacation"
        assert s3_data.content_type == S3ContentTypeEnum.PNG

    def test_to_cls_json_deserialization_without_key(self) -> None:
        """Test JSON deserialization handles missing key"""
        data = {
            "name": "photo.png",
            "content_type": "image/png",
        }
        s3_data = S3Data.to_cls(data)

        assert s3_data.name == "photo.png"
        assert s3_data.key is None
        assert s3_data.content_type == S3ContentTypeEnum.PNG


@pytest.mark.unit
class TestYouTubeVideoThumbnailPromptSuggesterJobData:
    """Test cases for YouTubeVideoThumbnailPromptSuggesterJobData model"""

    def test_to_json_includes_class_name(self) -> None:
        """Ensure name reflects the class name in JSON output."""
        data = YouTubeVideoThumbnailPromptSuggesterJobData(
            task_id=uuid4(),
            ref_id="sample_ref",
        )

        json_data = data.to_json()

        assert json_data["name"] == "YouTubeVideoThumbnailPromptSuggesterJobData"

    def test_to_cls_ignores_custom_name(self) -> None:
        """Ensure deserialization enforces the class name and ignores input overrides."""
        task_id = uuid4()

        loaded = YouTubeVideoThumbnailPromptSuggesterJobData.to_cls(
            {
                "task_id": str(task_id),
                "ref_id": "sample_ref",
                "name": "CustomName",
            }
        )
        assert loaded.name == "YouTubeVideoThumbnailPromptSuggesterJobData"


@pytest.mark.unit
class TestImageJobDataNames:
    """Ensure image JobData classes expose name metadata."""

    def test_image_prompt_job_data_name_reflection(self) -> None:
        data = ImagePromptJobData(
            task_id=uuid4(),
            description="thumbnail prompt",
            ref_id="sample_ref",
            image_type=ImageTypeEnum.YouTube,
        )

        assert data.to_json()["name"] == "ImagePromptJobData"

        loaded = ImagePromptJobData.to_cls(
            {
                "task_id": str(data.task_id),
                "description": "thumbnail prompt",
                "ref_id": "sample_ref",
                "image_type": ImageTypeEnum.YouTube.value,
                "name": "CustomName",
            }
        )
        assert loaded.name == "ImagePromptJobData"


@pytest.mark.unit
class TestPromptDBDataFields:
    """Ensure PromptDBData works with new inline structure."""

    def test_prompt_db_data_inline_fields(self) -> None:
        """Test that PromptDBData stores prompt fields inline."""
        from uuid import uuid4

        version_id = uuid4()
        prompt = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Test description",
            active_version=version_id,
            prompt="Test prompt",
            system_message="Test system message",
            ai=AIModelEnum.Grok,
            comment="Test comment",
        )

        assert prompt.prompt == "Test prompt"
        assert prompt.system_message == "Test system message"
        assert prompt.ai == AIModelEnum.Grok
        assert prompt.active_version == version_id
        assert prompt.task == PromptTaskEnum.YouTubeVideoSummarization

    def test_prompt_db_data_to_json(self) -> None:
        """Test that to_json produces the right fields."""
        from uuid import uuid4

        version_id = uuid4()
        prompt = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Test",
            active_version=version_id,
            prompt="p",
            system_message="s",
            ai=AIModelEnum.Grok,
        )
        data = prompt.to_json()
        assert data["active_version"] == str(version_id)
        assert data["prompt"] == "p"
        assert data["system_message"] == "s"
        assert data["ai"] == "Grok"
        assert "versions" not in data
        assert "response_data" not in data
        assert "prompt_data" in data
        assert data["prompt_data"] == []

    def test_prompt_db_data_to_cls(self) -> None:
        """Test round-trip to_json → to_cls."""
        from uuid import uuid4

        version_id = uuid4()
        original = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            description="Test",
            active_version=version_id,
            prompt="p",
            system_message="s",
            ai=AIModelEnum.Grok,
        )
        data = original.to_json()
        restored = PromptDBData.to_cls(data)
        assert restored.active_version == original.active_version
        assert restored.prompt == original.prompt
        assert restored.system_message == original.system_message
        assert restored.ai == original.ai
