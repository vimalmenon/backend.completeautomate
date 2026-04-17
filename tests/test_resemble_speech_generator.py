import os
from base64 import b64encode
from unittest.mock import MagicMock, patch

import pytest

from backend.ai.speech_generation.resemble_speech_generator import (
    ResembleSpeechGenerator,
)
from backend.exception.app_exception import AppException


@pytest.mark.unit
class TestResembleSpeechGenerator:
    @patch("backend.ai.speech_generation.resemble_speech_generator.Resemble")
    def test_generate_speech_returns_decoded_audio_bytes(
        self,
        mock_resemble: MagicMock,
    ) -> None:
        mock_resemble.v2.clips.create_direct.return_value = {
            "success": True,
            "audio_content": b64encode(b"audio-bytes").decode("utf-8"),
        }

        generator = ResembleSpeechGenerator(
            project_uuid="project-123",
            voice_uuid="voice-123",
        )

        result = generator.generate_speech("hello world")

        assert result == b"audio-bytes"
        mock_resemble.api_key.assert_called_once()
        mock_resemble.v2.clips.create_direct.assert_called_once_with(
            project_uuid="project-123",
            voice_uuid="voice-123",
            data="hello world",
            title=None,
            precision=None,
            output_format="wav",
            sample_rate=22050,
        )

    def test_generate_speech_raises_for_blank_text(self) -> None:
        generator = ResembleSpeechGenerator(
            project_uuid="project-123",
            voice_uuid="voice-123",
        )

        with pytest.raises(AppException, match="Text is required"):
            generator.generate_speech("   ")

    def test_generate_speech_raises_when_project_uuid_missing(self) -> None:
        generator = ResembleSpeechGenerator(project_uuid=None, voice_uuid="voice-123")

        with pytest.raises(AppException, match="project UUID is required"):
            generator.generate_speech("hello world")

    @patch.dict(os.environ, {"RESEMBLE_TTS_ID": ""}, clear=False)
    def test_generate_speech_raises_when_voice_uuid_missing(self) -> None:
        generator = ResembleSpeechGenerator(project_uuid="project-123", voice_uuid=None)

        with pytest.raises(AppException, match="voice UUID is required"):
            generator.generate_speech("hello world")

    @patch("backend.ai.speech_generation.resemble_speech_generator.Resemble")
    def test_generate_speech_raises_when_resemble_returns_error(
        self,
        mock_resemble: MagicMock,
    ) -> None:
        mock_resemble.v2.clips.create_direct.return_value = {
            "success": False,
            "message": "bad request",
        }

        generator = ResembleSpeechGenerator(
            project_uuid="project-123",
            voice_uuid="voice-123",
        )

        with pytest.raises(AppException, match="Resemble speech request failed"):
            generator.generate_speech("hello world")

    @patch("backend.ai.speech_generation.resemble_speech_generator.Resemble")
    @patch("backend.ai.speech_generation.resemble_speech_generator.urlopen")
    def test_generate_speech_downloads_audio_from_url(
        self,
        mock_urlopen: MagicMock,
        mock_resemble: MagicMock,
    ) -> None:
        mock_resemble.v2.clips.create_direct.return_value = {
            "success": True,
            "item": {"audio_src": "https://example.com/audio.wav"},
        }
        response = MagicMock()
        response.read.return_value = b"audio-from-url"
        mock_urlopen.return_value.__enter__.return_value = response

        generator = ResembleSpeechGenerator(
            project_uuid="project-123",
            voice_uuid="voice-123",
        )

        result = generator.generate_speech("hello world")

        assert result == b"audio-from-url"

    @patch("backend.ai.speech_generation.resemble_speech_generator.Resemble")
    def test_save_speech_persists_generated_audio(
        self,
        mock_resemble: MagicMock,
        tmp_path,
    ) -> None:
        mock_resemble.v2.clips.create_direct.return_value = {
            "success": True,
            "audio_content": b64encode(b"audio-bytes").decode("utf-8"),
        }
        target = tmp_path / "speech.wav"

        generator = ResembleSpeechGenerator(
            project_uuid="project-123",
            voice_uuid="voice-123",
        )
        saved_path = generator.save_speech("hello world", target)

        assert saved_path == target
        assert target.read_bytes() == b"audio-bytes"
