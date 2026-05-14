import base64
from pathlib import Path
from typing import Any, cast
from urllib.request import Request, urlopen

from resemble import Resemble

from backend.config.env import env
from backend.exception import AppException

RESEMBLE_PROJECT_ID_ENV_VARS = "34a0c33f"

RESEMBLE_VOICE_ID_ENV_VARS = "4e972f71"

DEFAULT_OUTPUT_FORMAT = "wav"
DEFAULT_SAMPLE_RATE = 48000
DEFAULT_PRECISION = "PCM_16"


class ResembleSpeechGenerator:
    """Resemble direct synthesis via the documented create_direct quickstart flow."""

    def __init__(
        self,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        precision: str | None = DEFAULT_PRECISION,
        title: str | None = None,
    ) -> None:
        self.api_key = str(env.RESEMBLE_API_KEY.get_secret_value())
        self.project_uuid = RESEMBLE_PROJECT_ID_ENV_VARS
        self.voice_uuid = RESEMBLE_VOICE_ID_ENV_VARS
        self.output_format = output_format
        self.sample_rate = sample_rate
        self.precision = precision
        self.title = title

        Resemble.api_key(self.api_key)

    def generate_speech(self, text: str) -> bytes:
        if not text or not text.strip():
            raise AppException("Text is required for speech generation")
        if not self.project_uuid:
            raise AppException(
                "Resemble project UUID is required. Set RESEMBLE_PROJECT_UUID or pass project_uuid."
            )
        if not self.voice_uuid:
            raise AppException(
                "Resemble voice UUID is required. Set RESEMBLE_VOICE_UUID or pass voice_uuid."
            )

        try:
            response = Resemble.v2.clips.create_direct(
                project_uuid=self.project_uuid,
                voice_uuid=self.voice_uuid,
                data=text,
                title=self.title,
                precision=self.precision,
                output_format=self.output_format,
                sample_rate=self.sample_rate,
            )
        except Exception as exc:
            raise AppException(f"Resemble speech generation error: {str(exc)}")

        return self._extract_audio_bytes(response)

    def save_speech(self, text: str, output_path: str | Path) -> Path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(self.generate_speech(text))
        return target_path

    def _extract_audio_bytes(self, response: Any) -> bytes:
        if not isinstance(response, dict):
            raise AppException("Unexpected Resemble response format")

        success = response.get("success")
        if success is False:
            message = (
                response.get("message") or response.get("error") or "Unknown error"
            )
            raise AppException(f"Resemble speech request failed: {message}")

        audio_content = response.get("audio_content")
        if isinstance(audio_content, str) and audio_content:
            try:
                return base64.b64decode(audio_content)
            except Exception as exc:
                raise AppException(f"Invalid Resemble audio payload: {str(exc)}")

        audio_url = self._extract_audio_url(response)
        if audio_url:
            request = Request(audio_url, headers={"User-Agent": "completeautomate/1.0"})
            with urlopen(request, timeout=30) as result:
                return cast(bytes, result.read())

        raise AppException("No audio data found in Resemble response.")

    def _extract_audio_url(self, response: dict[str, Any]) -> str | None:
        for key in ("audio_src", "result_audio_url", "audio_url"):
            value = response.get(key)
            if isinstance(value, str) and value:
                return value

        item = response.get("item")
        if not isinstance(item, dict):
            return None

        for key in ("audio_src", "result_audio_url", "audio_url"):
            value = item.get(key)
            if isinstance(value, str) and value:
                return value

        return None
