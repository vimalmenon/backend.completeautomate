"""Unit tests for AgentService"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.data.prompt import PromptDBData
from backend.enum import AIModelEnum, PromptTaskEnum, TeamEnum
from backend.exception.app_exception import AppException
from backend.services.agent_service import AgentService


@pytest.mark.unit
class TestAgentService:
    """Test cases for AgentService"""

    @patch("backend.services.agent_service.PromptDB")
    def test_get_prompt_renders_jinja_with_data(
        self, mock_prompt_db: MagicMock
    ) -> None:
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            prompt="Create 3 titles for {{ topic }} in {{ language }}.",
            system_message="You are a {{ role }} assistant.",
            describe="",
            task=PromptTaskEnum.YouTubeVideoAnalysis,
            role=TeamEnum.SOCIAL_MEDIA_MANAGER,
            ai=AIModelEnum.Grok,
            last_updated=datetime.now(),
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoAnalysis,
            task_id="123456",
            data={"topic": "Python testing", "language": "English", "role": "helpful"},
        )

        assert service.get_prompt() == "Create 3 titles for Python testing in English."
        assert service.get_system_message() == "You are a helpful assistant."

    @patch("backend.services.agent_service.PromptDB")
    def test_get_prompt_raises_for_missing_template_value(
        self, mock_prompt_db: MagicMock
    ) -> None:
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            prompt="Create a title about {{ topic }}",
            system_message="You are a content expert",
            task=PromptTaskEnum.YouTubeVideoAnalysis,
            role=TeamEnum.SOCIAL_MEDIA_MANAGER,
            ai=AIModelEnum.Grok,
            describe="",
            last_updated=datetime.now(),
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoAnalysis, task_id="123456", data={}
        )

        with pytest.raises(AppException, match="Error rendering prompt template"):
            service.get_prompt()
