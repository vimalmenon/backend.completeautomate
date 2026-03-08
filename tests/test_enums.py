"""Unit tests for enums"""

import pytest

from backend.enum.ai import AICreativityLevelEnum, AIModelEnum
from backend.enum.job import JobEnum
from backend.enum.s3 import S3ContentTypeEnum
from backend.enum.status import TaskStatusEnum
from backend.enum.team import TeamEnum


@pytest.mark.unit
class TestEnums:
    """Test cases for enum types"""

    def test_ai_model_enum(self) -> None:
        """Test AIModelEnum enum values"""
        assert AIModelEnum.Deepseek is not None
        assert AIModelEnum.Perplexity is not None
        assert AIModelEnum.Qwen is not None
        assert AIModelEnum.Grok is not None

    def test_ai_creativity_level_enum(self) -> None:
        """Test AICreativityLevelEnum enum values"""
        assert AICreativityLevelEnum.LOW is not None
        assert AICreativityLevelEnum.MEDIUM is not None
        assert AICreativityLevelEnum.HIGH is not None

    def test_job_enum(self) -> None:
        """Test JobEnum enum values"""
        assert JobEnum.ImageGenerator is not None
        assert JobEnum.ImagePrompt is not None
        assert JobEnum.YouTubeVideo is not None

    def test_s3_content_type_enum(self) -> None:
        """Test S3ContentTypeEnum enum values"""
        assert S3ContentTypeEnum.PNG is not None
        assert S3ContentTypeEnum.JPEG is not None
        assert S3ContentTypeEnum.JSON is not None

    def test_task_status_enum(self) -> None:
        """Test TaskStatusEnum enum values"""
        assert TaskStatusEnum.NEW is not None
        assert TaskStatusEnum.IN_PROGRESS is not None
        assert TaskStatusEnum.COMPLETED is not None
        assert TaskStatusEnum.FAILED is not None

    def test_enum_string_representation(self) -> None:
        """Test enum string representations"""
        assert str(TaskStatusEnum.NEW) != ""
        assert str(JobEnum.ImageGenerator) != ""

    def test_team_enum_role_and_display_name(self) -> None:
        """Test TeamEnum carries role and display_name metadata"""
        assert TeamEnum.OWNER.role == "Owner"
        assert TeamEnum.OWNER.display_name == "Vimal Menon"

    def test_team_enum_from_value_accepts_role(self) -> None:
        """Test TeamEnum.from_value resolves by role value"""
        assert TeamEnum.from_value("owner") == TeamEnum.OWNER
        assert TeamEnum.from_value("Owner") == TeamEnum.OWNER
        assert (
            TeamEnum.from_value("social-media-manager") == TeamEnum.SOCIAL_MEDIA_MANAGER
        )

    def test_team_enum_from_value_rejects_non_role_values(self) -> None:
        """TeamEnum.from_value should reject display names and enum names"""
        with pytest.raises(ValueError):
            TeamEnum.from_value("Vimal Menon")

        with pytest.raises(ValueError):
            TeamEnum.from_value("OWNER")
