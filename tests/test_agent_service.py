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


@pytest.mark.unit
class TestFewShotExamples:
    """Test suite for few-shot example injection in AgentService."""

    @patch("backend.services.agent_service.PromptDB")
    def test_get_prompt_appends_examples(self, mock_prompt_db: MagicMock) -> None:
        version_id = uuid4()
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoMetadata,
            description="",
            active_version=version_id,
            prompt="Create a title about {{ topic }}.",
            system_message="You are a helpful assistant.",
            ai=AIModelEnum.Grok,
            last_updated=datetime.now(),
            examples=[
                {"input": {"topic": "Cats"}, "output": "Top 10 Cat Facts"},
                {"input": {"topic": "Dogs"}, "output": "Why Dogs Are Amazing"},
            ],
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoMetadata,
            task_id="few-shot-1",
            data={"topic": "Python"},
        )

        result = service.get_prompt()

        assert "Create a title about Python." in result
        assert "Few-shot Examples:" in result
        assert "Example 1 Input" in result
        assert "Cats" in result
        assert "Top 10 Cat Facts" in result
        assert "Example 2 Input" in result
        assert "Dogs" in result
        assert "Why Dogs Are Amazing" in result

    @patch("backend.services.agent_service.PromptDB")
    def test_get_system_message_appends_examples(
        self, mock_prompt_db: MagicMock
    ) -> None:
        version_id = uuid4()
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoMetadata,
            description="",
            active_version=version_id,
            prompt="Create a title.",
            system_message="Respond in {{ language }}.",
            ai=AIModelEnum.Grok,
            last_updated=datetime.now(),
            examples=[
                {"input": "Hello", "output": "Hi"},
            ],
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoMetadata,
            task_id="few-shot-2",
            data={"language": "French"},
        )

        result = service.get_system_message()

        assert "Respond in French." in result
        assert "Few-shot Examples:" in result
        assert "Example 1 Input" in result

    @patch("backend.services.agent_service.PromptDB")
    def test_no_examples_when_list_empty(self, mock_prompt_db: MagicMock) -> None:
        version_id = uuid4()
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoMetadata,
            description="",
            active_version=version_id,
            prompt="Create a title about {{ topic }}.",
            system_message="You are helpful.",
            ai=AIModelEnum.Grok,
            last_updated=datetime.now(),
            examples=[],
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoMetadata,
            task_id="few-shot-3",
            data={"topic": "Python"},
        )

        result = service.get_prompt()
        assert result == "Create a title about Python."
        assert "Few-shot Examples:" not in result

    @patch("backend.services.agent_service.PromptDB")
    def test_examples_with_string_input(self, mock_prompt_db: MagicMock) -> None:
        version_id = uuid4()
        mock_prompt_db.return_value.get_prompt_by_task.return_value = PromptDBData(
            task=PromptTaskEnum.YouTubeVideoMetadata,
            description="",
            active_version=version_id,
            prompt="Create a title about {{ topic }}.",
            system_message="You are helpful.",
            ai=AIModelEnum.Grok,
            last_updated=datetime.now(),
            examples=[
                {"input": "simple string input", "output": "example output"},
            ],
        )

        service = AgentService(
            PromptTaskEnum.YouTubeVideoMetadata,
            task_id="few-shot-4",
            data={"topic": "Python"},
        )

        result = service.get_prompt()
        assert "simple string input" in result
        assert "example output" in result
