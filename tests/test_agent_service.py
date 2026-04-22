"""Unit tests for AgentService"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from backend.data.prompt import PromptDBData
from backend.enum import AIModelEnum, PromptTaskEnum
from backend.exception import AppException
from backend.services.agent_service import AgentService


@pytest.mark.unit
class TestAgentService:
    """Test cases for AgentService"""

    @patch("backend.services.agent_service.PromptDB")
    def test_get_prompt_renders_jinja_with_data(
        self, mock_prompt_db: MagicMock
    ) -> None:
        from uuid import uuid4

        from backend.data.prompt import PromptVersionDBData

        version_id = uuid4()
        version = PromptVersionDBData(
            prompt="Create 3 titles for {{ topic }} in {{ language }}.",
            system_message="You are a {{ role }} assistant.",
            version=version_id,
            ai=AIModelEnum.Grok,
        )
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoMetadata,
            description="",
            versions=[version],
            version=version_id,
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
        from uuid import uuid4

        from backend.data.prompt import PromptVersionDBData

        version_id = uuid4()
        version = PromptVersionDBData(
            prompt="Create a title about {{ topic }}",
            system_message="You are a content expert",
            version=version_id,
            ai=AIModelEnum.Grok,
        )
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoMetadata,
            description="",
            versions=[version],
            version=version_id,
            last_updated=datetime.now(),
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoMetadata, task_id="123456", data={}
        )

        with pytest.raises(AppException, match="Error rendering prompt template"):
            service.get_prompt()
