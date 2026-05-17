"""Tests for AgentService"""
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from backend.data.prompt import PromptDBData
from backend.enum import AIModelEnum
from backend.enum.prompt import PromptTaskEnum
from backend.services.agent_service import AgentService


@pytest.mark.unit
class TestAgentService:
    """Test suite for AgentService."""

    @patch("backend.services.agent_service.PromptDB")
    def test_get_prompt_renders_jinja_with_data(
        self, mock_prompt_db: MagicMock
    ) -> None:
        version_id = uuid4()
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoMetadata,
            description="",
            active_version=version_id,
            prompt="Create 3 titles for {{ topic }} in {{ language }}.",
            system_message="You are a {{ role }} assistant.",
            ai=AIModelEnum.Grok,
            last_updated=datetime.now(),
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoMetadata,
            task_id="123456",
            data={"topic": "Python testing", "language": "English", "role": "helpful"},
        )

        assert service.get_prompt() == "Create 3 titles for Python testing in English."
        assert service.get_system_message() == "You are a helpful assistant."

    @patch("backend.services.agent_service.PromptDB")
    def test_get_prompt_raises_for_missing_template_value(
        self, mock_prompt_db: MagicMock
    ) -> None:
        version_id = uuid4()
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoMetadata,
            description="",
            active_version=version_id,
            prompt="Create a title about {{ topic }}",
            system_message="You are a content expert",
            ai=AIModelEnum.Grok,
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoMetadata,
            task_id="789012",
            data={},
        )

        with pytest.raises(Exception, match="undefined"):
            service.get_prompt()
