import base64
import os
from pathlib import Path
from typing import Any, cast
from urllib.request import Request, urlopen

from resemble import Resemble

from backend.config.env import env
from backend.exception.app_exception import AppException

RESEMBLE_PROJECT_ID_ENV_VARS = (
    "RESEMBLE_PROJECT_UUID",
    "RESEMBLE_PROJECT_ID",
)
RESEMBLE_VOICE_ID_ENV_VARS = (
    "RESEMBLE_VOICE_UUID",
    "RESEMBLE_VOICE_ID",
    "RESEMBLE_TTS_ID",
)


class ResembleSpeechGenerator:
    def __init__(
        self,
        project_uuid: str | None = None,
        voice_uuid: str | None = None,
        output_format: str = "wav",
        sample_rate: int = 22050,
        precision: str | None = None,
        title: str | None = None,
    ) -> None:
        self.api_key = str(env.RESEMBLE_API_KEY.get_secret_value())
        self.project_uuid = project_uuid or self._get_env_value(
            RESEMBLE_PROJECT_ID_ENV_VARS
        )
        self.voice_uuid = voice_uuid or self._get_env_value(RESEMBLE_VOICE_ID_ENV_VARS)
        self.output_format = output_format
        self.sample_rate = sample_rate
        self.precision = precision
        self.title = title

        Resemble.api_key(self.api_key)

    def generate_speech(self, text: str) -> bytes:
        if not text or not text.strip():
            raise AppException("Text is required for speech generation")
        if not self.project_uuid:
            raise AppException("Resemble project UUID is required")
        if not self.voice_uuid:
            raise AppException("Resemble voice UUID is required")

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

    def _get_env_value(self, names: tuple[str, ...]) -> str | None:
        for name in names:
            value = os.environ.get(name)
            if value:
                return value
        return None
