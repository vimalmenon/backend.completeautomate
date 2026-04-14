from http import HTTPStatus
from pathlib import Path
from typing import Any

import dashscope
from dashscope import SpeechSynthesizer

from backend.config.env import env
from backend.exception.app_exception import AppException


class QwenSpeechGenerator:
    """Qwen speech generation via Alibaba Cloud DashScope SDK."""

    def __init__(
        self,
        model: str = "qwen-tts",
        audio_format: str = SpeechSynthesizer.AudioFormat.format_mp3,
        voice: str | None = None,
        sample_rate: int | None = None,
        volume: int = 50,
        rate: float = 1.0,
        pitch: float = 1.0,
        word_timestamp_enabled: bool = False,
        phoneme_timestamp_enabled: bool = False,
    ):
        self.model = model
        self.audio_format = audio_format
        self.voice = voice
        self.sample_rate = sample_rate
        self.volume = volume
        self.rate = rate
        self.pitch = pitch
        self.word_timestamp_enabled = word_timestamp_enabled
        self.phoneme_timestamp_enabled = phoneme_timestamp_enabled

        dashscope.api_key = str(env.QWEN_API_KEY.get_secret_value())
        dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

    def generate_speech(self, text: str) -> bytes:
        """Generate speech audio bytes from text."""
        if not text or not text.strip():
            raise AppException("Text is required for speech generation")

        try:
            result = SpeechSynthesizer.call(
                model=self.model,
                text=text,
                format=self.audio_format,
                voice=self.voice,
                sample_rate=self.sample_rate,
                volume=self.volume,
                rate=self.rate,
                pitch=self.pitch,
                word_timestamp_enabled=self.word_timestamp_enabled,
                phoneme_timestamp_enabled=self.phoneme_timestamp_enabled,
            )
        except Exception as e:
            raise AppException(f"Qwen speech generation error: {str(e)}")

        return self._extract_audio_bytes(result)

    def save_speech(self, text: str, output_path: str | Path) -> Path:
        """Generate speech and persist it to disk."""
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(self.generate_speech(text))
        return target_path

    def _extract_audio_bytes(self, result: Any) -> bytes:
        response = self._extract_response(result)
        if response is not None:
            status_code = self._get_response_value(response, "status_code")
            if status_code not in (None, HTTPStatus.OK):
                error_message = self._get_response_value(
                    response,
                    "message",
                ) or self._get_response_value(response, "code")
                raise AppException(
                    f"DashScope speech request failed: {error_message or 'Unknown DashScope error'}"
                )

        audio_data = (
            result.get_audio_data() if hasattr(result, "get_audio_data") else None
        )
        if not isinstance(audio_data, (bytes, bytearray)) or not audio_data:
            raise AppException("No audio data found in Qwen speech response.")

        return bytes(audio_data)

    def _extract_response(self, result: Any) -> Any:
        if hasattr(result, "get_response"):
            return result.get_response()
        return None

    def _get_response_value(self, response: Any, key: str) -> Any:
        value = getattr(response, key, None)
        if value is not None:
            return value
        if hasattr(response, "get"):
            return response.get(key)
        return None
