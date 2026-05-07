import os
from pathlib import Path
from typing import Any, Protocol

from backend.exception import AppException

MANUS_API_KEY_ENV_VARS = ("MANUS_API_KEY",)
DEFAULT_OUTPUT_FORMAT = "mp4"
DEFAULT_MODEL = "manus-avatar-v1"


class ManusVideoClient(Protocol):
    def generate_video(
        self,
        *,
        prompt: str,
        model: str,
        output_format: str,
    ) -> bytes | dict[str, Any]: ...


class ManusVideoGenerator:
    """Scaffolded Manus video provider.

    The transport layer is intentionally injected so the provider contract can be
    stabilized now and the real Manus SDK/API details can be filled in later.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        client: ManusVideoClient | None = None,
    ) -> None:
        self.api_key = api_key or self._get_env_value(MANUS_API_KEY_ENV_VARS)
        self.model = model
        self.output_format = output_format
        self.client = client

    def generate_video(self, prompt: str) -> bytes:
        if not prompt or not prompt.strip():
            raise AppException("Prompt is required for video generation")
        if not self.api_key:
            raise AppException(
                "Manus API key is required. Set MANUS_API_KEY or pass api_key."
            )
        if self.client is None:
            raise AppException(
                "Manus client is not configured. Provide a client adapter until the live API is wired."
            )

        try:
            response = self.client.generate_video(
                prompt=prompt,
                model=self.model,
                output_format=self.output_format,
            )
        except Exception as exc:
            raise AppException(f"Manus video generation error: {str(exc)}") from exc

        return self._extract_video_bytes(response)

    def save_video(self, prompt: str, output_path: str | Path) -> Path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(self.generate_video(prompt))
        return target_path

    def _extract_video_bytes(self, response: bytes | dict[str, Any]) -> bytes:
        if isinstance(response, bytes):
            if response:
                return response
            raise AppException("No video data found in Manus response")

        if not isinstance(response, dict):
            raise AppException("Unexpected Manus response format")

        for key in ("video_bytes", "content", "data"):
            value = response.get(key)
            if isinstance(value, bytes) and value:
                return value

        raise AppException("No video data found in Manus response")

    def _get_env_value(self, names: tuple[str, ...]) -> str | None:
        for name in names:
            value = os.environ.get(name)
            if value:
                return value
        return None
