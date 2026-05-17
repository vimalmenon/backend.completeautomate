"""Unit tests for Prompt Manager"""
from unittest.mock import patch
from uuid import uuid4

import pytest

from backend.data import PromptDBData, PromptVersionDBData
from backend.data.api import PromptUpdateResult
from backend.enum import AIModelEnum
from backend.enum.prompt import PromptTaskEnum
from backend.exception import AppException
from backend.manager import PromptManager


@pytest.mark.unit
def test_add_prompt_persists_first_version() -> None:
    with patch("backend.manager.prompt_manager.PromptDB") as mock_prompt_db_cls:
        mock_prompt_db = mock_prompt_db_cls.return_value
        mock_prompt_db.get_prompt_by_task.return_value = None

        result = PromptManager().add_prompt(
            data=PromptUpdateResult(
                task=PromptTaskEnum.YouTubeVideoSummarization,
                description="New description",
                comment="New comment",
                prompt="New prompt",
                system_message="New system message",
                ai=AIModelEnum.Grok,
            )
        )

    mock_prompt_db.save_prompt.assert_called_once()
    saved_prompt = mock_prompt_db.save_prompt.call_args.kwargs["data"]

    assert result.task == PromptTaskEnum.YouTubeVideoSummarization
    assert result.description == "New description"
    assert result.comment == "New comment"
    assert result.prompt == "New prompt"
    assert result.system_message == "New system message"
    assert result.ai == AIModelEnum.Grok
    assert saved_prompt.task == PromptTaskEnum.YouTubeVideoSummarization
    assert saved_prompt.description == "New description"
    assert saved_prompt.prompt == "New prompt"


@pytest.mark.unit
def test_add_prompt_raises_when_task_exists() -> None:
    existing_version = uuid4()
    existing_prompt = PromptDBData(
        task=PromptTaskEnum.YouTubeVideoSummarization,
        description="Existing description",
        active_version=existing_version,
        prompt="Existing prompt",
        system_message="Existing system message",
        ai=AIModelEnum.Deepseek,
    )

    with patch("backend.manager.prompt_manager.PromptDB") as mock_prompt_db_cls:
        mock_prompt_db = mock_prompt_db_cls.return_value
        mock_prompt_db.get_prompt_by_task.return_value = existing_prompt

        with pytest.raises(AppException, match="Prompt already exists"):
            PromptManager().add_prompt(
                data=PromptUpdateResult(
                    task=PromptTaskEnum.YouTubeVideoSummarization,
                    description="New description",
                    prompt="New prompt",
                    system_message="New system message",
                    ai=AIModelEnum.Grok,
                )
            )

    mock_prompt_db.save_prompt.assert_not_called()


@pytest.mark.unit
def test_update_prompt_creates_new_active_version() -> None:
    version_id = uuid4()
    original_prompt = PromptDBData(
        task=PromptTaskEnum.YouTubeVideoSummarization,
        description="Original description",
        active_version=version_id,
        prompt="Original prompt",
        system_message="Original system message",
        ai=AIModelEnum.Deepseek,
        comment="Original comment",
    )
    update_version_id = uuid4()

    with patch("backend.manager.prompt_manager.PromptDB") as mock_prompt_db_cls:
        mock_prompt_db = mock_prompt_db_cls.return_value
        mock_prompt_db.get_prompt_by_task.return_value = original_prompt

        result = PromptManager().update_prompt(
            task=PromptTaskEnum.YouTubeVideoSummarization,
            data=PromptUpdateResult(
                task=PromptTaskEnum.YouTubeVideoSummarization,
                description="Updated description",
                comment="Updated comment",
                prompt="Updated prompt",
                system_message="Updated system message",
                ai=AIModelEnum.Grok,
                version=update_version_id,
            ),
        )

    mock_prompt_db.update_prompt.assert_called_once()
    persisted_values = mock_prompt_db.update_prompt.call_args.kwargs["values"]

    assert result.active_version == update_version_id
    assert result.description == "Updated description"
    assert result.comment == "Updated comment"
    assert result.prompt == "Updated prompt"
    assert result.system_message == "Updated system message"
    assert result.ai == AIModelEnum.Grok
    assert persisted_values["active_version"] == str(update_version_id)
    assert persisted_values["description"] == "Updated description"
    assert persisted_values["comment"] == "Updated comment"


@pytest.mark.unit
def test_update_prompt_raises_when_task_missing() -> None:
    with patch("backend.manager.prompt_manager.PromptDB") as mock_prompt_db_cls:
        mock_prompt_db = mock_prompt_db_cls.return_value
        mock_prompt_db.get_prompt_by_task.return_value = None

        with pytest.raises(AppException, match="Prompt not found"):
            PromptManager().update_prompt(
                task=PromptTaskEnum.YouTubeVideoSummarization,
                data=PromptUpdateResult(
                    task=PromptTaskEnum.YouTubeVideoSummarization,
                    description="Updated description",
                    prompt="Updated prompt",
                    system_message="Updated system message",
                    ai=AIModelEnum.Grok,
                ),
            )

    mock_prompt_db.update_prompt.assert_not_called()
