from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from backend.ai.speech_generation import QwenSpeechGenerator
from backend.exception.app_exception import AppException


@pytest.mark.unit
class TestQwenSpeechGenerator:
    @patch("backend.ai.speech_generation.qwen_speech_generator.SpeechSynthesizer")
    def test_generate_speech_returns_audio_bytes(
        self,
        mock_speech_synthesizer: MagicMock,
    ) -> None:
        mock_result = MagicMock()
        mock_result.get_audio_data.return_value = b"audio-bytes"
        mock_result.get_response.return_value = SimpleNamespace(
            status_code=200,
            message="ok",
        )
        mock_speech_synthesizer.call.return_value = mock_result

        generator = QwenSpeechGenerator()
        result = generator.generate_speech("hello world")

        assert result == b"audio-bytes"
        mock_speech_synthesizer.call.assert_called_once()

    def test_generate_speech_raises_for_blank_text(self) -> None:
        generator = QwenSpeechGenerator()

        with pytest.raises(AppException, match="Text is required"):
            generator.generate_speech("   ")

    @patch("backend.ai.speech_generation.qwen_speech_generator.SpeechSynthesizer")
    def test_generate_speech_raises_when_dashscope_returns_error(
        self,
        mock_speech_synthesizer: MagicMock,
    ) -> None:
        mock_result = MagicMock()
        mock_result.get_audio_data.return_value = b""
        mock_result.get_response.return_value = SimpleNamespace(
            status_code=500,
            message="bad request",
        )
        mock_speech_synthesizer.call.return_value = mock_result

        generator = QwenSpeechGenerator()

        with pytest.raises(AppException, match="DashScope speech request failed"):
            generator.generate_speech("hello world")

    @patch("backend.ai.speech_generation.qwen_speech_generator.SpeechSynthesizer")
    def test_generate_speech_raises_when_audio_missing(
        self,
        mock_speech_synthesizer: MagicMock,
    ) -> None:
        mock_result = MagicMock()
        mock_result.get_audio_data.return_value = None
        mock_result.get_response.return_value = SimpleNamespace(
            status_code=200,
            message="ok",
        )
        mock_speech_synthesizer.call.return_value = mock_result

        generator = QwenSpeechGenerator()

        with pytest.raises(AppException, match="No audio data found"):
            generator.generate_speech("hello world")
