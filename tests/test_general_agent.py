"""Unit tests for GeneralAgent integration"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from langchain.messages import AIMessage, HumanMessage, SystemMessage

from backend.data import MessageDBData
from backend.enum import TeamEnum
from backend.exception import AppException
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


def _build_agent_service_mock() -> MagicMock:
    service = MagicMock(spec=AgentService)
    service.task_id = "task-1"
    service.prompt_data = SimpleNamespace(role=TeamEnum.MANAGER)
    service.get_prompt.return_value = "Write test cases"
    service.get_system_message.return_value = "You are a helpful manager"
    service.get_model.return_value = "test-model"
    return service


@pytest.mark.unit
class TestGeneralAgent:

    @patch("backend.integration.agent.general_agent.AgentMessageDB")
    @patch("backend.integration.agent.general_agent.create_agent")
    def test_invoke_saves_messages(
        self, mock_create_agent: MagicMock, mock_agent_db_cls: MagicMock
    ) -> None:
        service = _build_agent_service_mock()
        runtime_agent = MagicMock()
        runtime_agent.invoke.return_value = {
            "messages": [
                SystemMessage(content="You are a helpful manager"),
                HumanMessage(content="Write test cases"),
                AIMessage(content="Sure, here are tests"),
            ]
        }
        mock_create_agent.return_value = runtime_agent

        general_agent = GeneralAgent(service)
        result = general_agent.invoke()

        assert result["messages"][-1].content == "Sure, here are tests"
        mock_create_agent.assert_called_once_with(
            model="test-model",
            response_format=None,
        )
        mock_agent_db_cls.return_value.save_message.assert_called_once()

    @patch("backend.integration.agent.general_agent.AgentMessageDB")
    @patch("backend.integration.agent.general_agent.create_agent")
    def test_reinvoke_updates_messages(
        self, mock_create_agent: MagicMock, mock_agent_db_cls: MagicMock
    ) -> None:
        service = _build_agent_service_mock()
        runtime_agent = MagicMock()
        runtime_agent.invoke.return_value = {
            "messages": [
                SystemMessage(content="You are a helpful manager"),
                HumanMessage(content="Write test cases"),
                AIMessage(content="Done"),
            ]
        }
        mock_create_agent.return_value = runtime_agent
        mock_agent_db_cls.return_value.get_messages_by_task_id.return_value = (
            MessageDBData(
                task_id="task-1",
                messages=[
                    {"role": "system", "content": "You are a helpful manager"},
                    {"role": "human", "content": "Write test cases"},
                    {"role": "ai", "content": "Done"},
                ],
            )
        )

        general_agent = GeneralAgent(service)
        general_agent.reinvoke("Refine the answer")

        invoke_arg = runtime_agent.invoke.call_args[0][0]
        assert invoke_arg["messages"][-1].content == "Refine the answer"
        mock_agent_db_cls.return_value.update_message.assert_called_once()

    @patch("backend.integration.agent.general_agent.AgentMessageDB")
    def test_reinvoke_raises_when_no_stored_messages(
        self, mock_agent_db_cls: MagicMock
    ) -> None:
        service = _build_agent_service_mock()
        mock_agent_db_cls.return_value.get_messages_by_task_id.return_value = None

        general_agent = GeneralAgent(service)

        with pytest.raises(AppException, match="data not found"):
            general_agent.reinvoke("Refine the answer")

    def test_init_raises_when_prompt_data_missing(self) -> None:
        service = MagicMock(spec=AgentService)
        service.task_id = "task-1"
        service.prompt_data = None

        with pytest.raises(AppException, match="Prompt data is required"):
            GeneralAgent(service)
