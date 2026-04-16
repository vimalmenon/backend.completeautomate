import base64
import threading
from pathlib import Path
from typing import Any

import dashscope
from dashscope.audio.qwen_tts_realtime import (
    AudioFormat,
    QwenTtsRealtime,
    QwenTtsRealtimeCallback,
)

from backend.config.env import env
from backend.exception.app_exception import AppException

QWEN_HTTP_API_URL = "https://dashscope-intl.aliyuncs.com/api/v1"
QWEN_WEBSOCKET_API_URL = "wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime"


class _SpeechCollectionCallback(QwenTtsRealtimeCallback):
    def __init__(self) -> None:
        self.audio_chunks: list[bytes] = []
        self.completed = threading.Event()
        self.error_message: str | None = None

    def on_close(self, close_status_code, close_msg) -> None:
        if close_status_code not in (None, 1000) and self.error_message is None:
            self.error_message = f"WebSocket closed: {close_status_code} {close_msg}"
        self.completed.set()

    def on_event(self, message: dict[str, Any]) -> None:
        event_type = message.get("type")
        if event_type == "response.audio.delta":
            delta = message.get("delta")
            if isinstance(delta, str) and delta:
                self.audio_chunks.append(base64.b64decode(delta))
            return

        if event_type == "error":
            error = message.get("error", {})
            if isinstance(error, dict):
                self.error_message = error.get("message") or error.get("code")
            else:
                self.error_message = str(error)
            self.completed.set()
            return

        if event_type == "session.finished":
            self.completed.set()

    def get_audio(self) -> bytes:
        return b"".join(self.audio_chunks)


class QwenSpeechGenerator:
    """Qwen speech generation via Alibaba Cloud DashScope SDK."""

    def __init__(
        self,
        model: str = "qwen3-tts-instruct-flash-realtime",
        audio_format: str = "mp3",
        voice: str | None = "Cherry",
        sample_rate: int | None = None,
        volume: int = 50,
        rate: float = 1.0,
        pitch: float = 1.0,
        instructions: str | None = None,
        optimize_instructions: bool = True,
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
        self.instructions = instructions
        self.optimize_instructions = optimize_instructions
        self.word_timestamp_enabled = word_timestamp_enabled
        self.phoneme_timestamp_enabled = phoneme_timestamp_enabled
        self.api_key = str(env.QWEN_API_KEY.get_secret_value())
        dashscope.api_key = self.api_key
        dashscope.base_http_api_url = QWEN_HTTP_API_URL
        dashscope.base_websocket_api_url = QWEN_WEBSOCKET_API_URL

    def generate_speech(self, text: str) -> bytes:
        """Generate speech audio bytes from text."""
        if not text or not text.strip():
            raise AppException("Text is required for speech generation")

        callback = _SpeechCollectionCallback()
        synthesizer = QwenTtsRealtime(
            model=self.model,
            callback=callback,
            url=QWEN_WEBSOCKET_API_URL,
        )

        try:
            synthesizer.connect()
            synthesizer.update_session(
                voice=self.voice or "Cherry",
                response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
                sample_rate=self.sample_rate,
                volume=self.volume,
                speech_rate=self.rate,
                audio_format=self.audio_format,
                pitch_rate=self.pitch,
                instructions=self.instructions,
                optimize_instructions=self.optimize_instructions,
            )
            synthesizer.append_text(text)
            synthesizer.finish()
            if not callback.completed.wait(timeout=180):
                raise AppException("Timed out waiting for Qwen speech generation")
        except Exception as e:
            raise AppException(f"Qwen speech generation error: {str(e)}")
        finally:
            if synthesizer.ws is not None:
                synthesizer.close()

        return self._extract_audio_bytes(callback)

    def save_speech(self, text: str, output_path: str | Path) -> Path:
        """Generate speech and persist it to disk."""
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(self.generate_speech(text))
        return target_path

    def _extract_audio_bytes(self, callback: _SpeechCollectionCallback) -> bytes:
        if callback.error_message:
            raise AppException(
                f"DashScope speech request failed: {callback.error_message}"
            )

        audio_data = callback.get_audio()
        if not audio_data:
            raise AppException("No audio data found in Qwen speech response.")

        return audio_data
