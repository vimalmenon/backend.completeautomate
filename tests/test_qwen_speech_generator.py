from unittest.mock import MagicMock, patch

import pytest

from backend.ai.speech_generation import QwenSpeechGenerator
from backend.ai.speech_generation.qwen_speech_generator import (
    _SpeechCollectionCallback,
)
from backend.exception.app_exception import AppException


@pytest.mark.unit
class TestQwenSpeechGenerator:
    @patch("backend.ai.speech_generation.qwen_speech_generator.QwenTtsRealtime")
    def test_generate_speech_returns_audio_bytes(
        self,
        mock_qwen_tts_realtime: MagicMock,
    ) -> None:
        mock_synthesizer = MagicMock()

        def connect_side_effect() -> None:
            callback = mock_qwen_tts_realtime.call_args.kwargs["callback"]
            callback.on_event({"type": "response.audio.delta", "delta": "YXVkaW8t"})
            callback.on_event({"type": "response.audio.delta", "delta": "Ynl0ZXM="})
            callback.on_event({"type": "session.finished"})

        mock_synthesizer.connect.side_effect = connect_side_effect
        mock_synthesizer.ws = object()
        mock_qwen_tts_realtime.return_value = mock_synthesizer

        generator = QwenSpeechGenerator()
        result = generator.generate_speech("hello world")

        assert result == b"audio-bytes"
        mock_qwen_tts_realtime.assert_called_once()
        mock_synthesizer.update_session.assert_called_once()
        mock_synthesizer.append_text.assert_called_once_with("hello world")
        mock_synthesizer.finish.assert_called_once()
        mock_synthesizer.close.assert_called_once()

    def test_generate_speech_raises_for_blank_text(self) -> None:
        generator = QwenSpeechGenerator()

        with pytest.raises(AppException, match="Text is required"):
            generator.generate_speech("   ")

    @patch("backend.ai.speech_generation.qwen_speech_generator.QwenTtsRealtime")
    def test_generate_speech_raises_when_dashscope_returns_error(
        self,
        mock_qwen_tts_realtime: MagicMock,
    ) -> None:
        mock_synthesizer = MagicMock()

        def connect_side_effect() -> None:
            callback = mock_qwen_tts_realtime.call_args.kwargs["callback"]
            callback.on_event(
                {
                    "type": "error",
                    "error": {"message": "bad request"},
                }
            )

        mock_synthesizer.connect.side_effect = connect_side_effect
        mock_synthesizer.ws = object()
        mock_qwen_tts_realtime.return_value = mock_synthesizer

        generator = QwenSpeechGenerator()

        with pytest.raises(AppException, match="DashScope speech request failed"):
            generator.generate_speech("hello world")

    @patch("backend.ai.speech_generation.qwen_speech_generator.QwenTtsRealtime")
    def test_generate_speech_raises_when_audio_missing(
        self,
        mock_qwen_tts_realtime: MagicMock,
    ) -> None:
        mock_synthesizer = MagicMock()

        def connect_side_effect() -> None:
            callback = mock_qwen_tts_realtime.call_args.kwargs["callback"]
            callback.on_event({"type": "session.finished"})

        mock_synthesizer.connect.side_effect = connect_side_effect
        mock_synthesizer.ws = object()
        mock_qwen_tts_realtime.return_value = mock_synthesizer

        generator = QwenSpeechGenerator()

        with pytest.raises(AppException, match="No audio data found"):
            generator.generate_speech("hello world")

    def test_callback_stores_websocket_close_error(self) -> None:
        callback = _SpeechCollectionCallback()

        callback.on_close(1006, "abnormal closure")

        assert callback.error_message == "WebSocket closed: 1006 abnormal closure"
        assert callback.completed.is_set()
