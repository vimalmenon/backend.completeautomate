from unittest.mock import MagicMock, patch

import pytest

from backend.enum import AIVideoModelEnum
from backend.exception import AppException
from backend.services.video_service import AgentVideoService


@pytest.mark.unit
class TestAgentVideoService:
    @patch("backend.services.video_service.ManusVideoGenerator")
    def test_get_model_returns_manus_generator(
        self,
        mock_generator: MagicMock,
    ) -> None:
        service = AgentVideoService(
            prompt="avatar prompt",
            video_ai=AIVideoModelEnum.Manus,
        )

        result = service.get_model()

        assert result == mock_generator.return_value
        mock_generator.assert_called_once_with()

    def test_get_prompt_returns_prompt(self) -> None:
        service = AgentVideoService(prompt="avatar prompt")

        assert service.get_prompt() == "avatar prompt"

    def test_get_model_raises_for_unsupported_model(self) -> None:
        service = AgentVideoService(prompt="avatar prompt", video_ai="Other")

        with pytest.raises(AppException, match="Unsupported AI model"):
            service.get_model()