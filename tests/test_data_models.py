"""Unit tests for data models"""

from uuid import uuid4

import pytest

from backend.data.image import ImagePromptJobData
from backend.data.prompt import PromptDBData
from backend.data.s3 import S3Data
from backend.data.youtube_channel import (
    YouTubeJobData,
    YouTubeThumbnailJobData,
    YouTubeVideoMetadataJobData,
    YouTubeVideoSummarizeJobData,
    YouTubeVideoThumbnailPromptSuggesterJobData,
)
from backend.enum import AIModelEnum, ImageTypeEnum
from backend.enum.prompt import PromptTaskEnum
from backend.enum.s3 import S3ContentTypeEnum
from backend.enum.status import TaskStatusEnum
from backend.enum.team import TeamEnum


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
class TestYouTubeJobDataNames:
    """Ensure all YouTube JobData classes reflect name in JSON and deserialization."""

    def test_youtube_thumbnail_job_data_name_reflection(self) -> None:
        data = YouTubeThumbnailJobData(
            data=S3Data(name="test.png", content_type=S3ContentTypeEnum.PNG),
            status=TaskStatusEnum.NEW,
            ref_id="sample_ref",
        )
        assert data.to_json()["name"] == "YouTubeThumbnailJobData"

        loaded = YouTubeThumbnailJobData.to_cls(
            {
                "data": data.data.to_json(),
                "status": TaskStatusEnum.NEW.value,
                "ref_id": "sample_ref",
                "name": "CustomName",
            }
        )
        assert loaded.name == "YouTubeThumbnailJobData"

    def test_youtube_job_data_name_reflection(self) -> None:
        data = YouTubeJobData(ref_id="sample_ref")
        assert data.to_json()["name"] == "YouTubeJobData"

        loaded = YouTubeJobData.to_cls({"ref_id": "sample_ref", "name": "CustomName"})
        assert loaded.name == "YouTubeJobData"

    def test_youtube_video_summarize_job_data_name_reflection(self) -> None:
        data = YouTubeVideoSummarizeJobData(ref_id="sample_ref")
        assert data.to_json()["name"] == "YouTubeVideoSummarizeJobData"

        loaded = YouTubeVideoSummarizeJobData.to_cls(
            {"ref_id": "sample_ref", "name": "CustomName"}
        )
        assert loaded.name == "YouTubeVideoSummarizeJobData"

    def test_youtube_video_metadata_job_data_name_reflection(self) -> None:
        data = YouTubeVideoMetadataJobData(
            task_id=uuid4(),
            ref_id="sample_ref",
            title="Sample Title",
            description="Sample Description",
            tags=["tag1", "tag2"],
        )
        assert data.to_json()["name"] == "YouTubeVideoMetadataJobData"

        loaded = YouTubeVideoMetadataJobData.to_cls(
            {
                "task_id": str(data.task_id),
                "ref_id": "sample_ref",
                "title": "Sample Title",
                "description": "Sample Description",
                "tags": ["tag1", "tag2"],
                "name": "CustomName",
            }
        )
        assert loaded.name == "YouTubeVideoMetadataJobData"


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
class TestPromptDBDataCopy:
    """Ensure PromptDBData.copy() creates proper shallow copies."""

    def test_prompt_db_data_copy(self) -> None:
        """Test that copy creates a new instance with same values."""
        original = PromptDBData(
            prompt="test prompt",
            system_message="test system message",
            task=PromptTaskEnum.YouTubeVideoSummarization,
            role=TeamEnum.OWNER,
            ai=AIModelEnum.Grok,
            version="1.0",
        )

        # Create a copy
        copied = original.copy()

        # Verify it's a different object
        assert copied is not original

        # Verify all values are the same
        assert copied.prompt == original.prompt
        assert copied.system_message == original.system_message
        assert copied.task == original.task
        assert copied.role == original.role
        assert copied.ai == original.ai
        assert copied.version == original.version
        assert copied.last_updated == original.last_updated

    def test_prompt_db_data_copy_modification(self) -> None:
        """Test that modifying copy doesn't affect original."""
        original = PromptDBData(
            prompt="test prompt",
            system_message="test system message",
            task=PromptTaskEnum.YouTubeVideoAnalysis,
            role=TeamEnum.OWNER,
            ai=AIModelEnum.Deepseek,
            version="1.0",
        )

        # Create a copy
        copied = original.copy()

        # Modify the copy
        copied.ai = AIModelEnum.Grok

        # Verify original is unchanged
        assert original.ai == AIModelEnum.Deepseek
        assert copied.ai == AIModelEnum.Grok
