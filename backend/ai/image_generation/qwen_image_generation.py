import base64
import binascii
from http import HTTPStatus
from typing import Any, cast
from urllib.request import Request, urlopen

import dashscope
from dashscope import MultiModalConversation

from backend.config.env import env
from backend.exception.app_exception import AppException


class QwenImageGeneration:
    """Qwen image generation via Alibaba Cloud DashScope SDK."""

    def __init__(
        self,
        model: str = "qwen-image-max",
        # TODO Need to fix this size hardcoding. Qwen image generation supports multiple sizes, and we should allow callers to specify desired size.
        size: str = "1328*1328",
    ):
        self.model = model
        self.size = size
        dashscope.api_key = str(env.QWEN_API_KEY.get_secret_value())
        dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

    def generate(self, prompt: str) -> bytes:
        """Generate an image from text prompt and return image bytes."""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ]
            response = MultiModalConversation.call(
                api_key=str(env.QWEN_API_KEY.get_secret_value()),
                model=self.model,
                messages=messages,
                result_format="message",
                stream=False,
                watermark=False,
                prompt_extend=True,
                negative_prompt="",
                size=self.size,
            )
            return self._parse_response(response)
        except Exception as e:
            raise AppException(f"Qwen image generation error: {str(e)}")

    def _parse_response(self, response: Any) -> bytes:
        if getattr(response, "status_code", None) != HTTPStatus.OK:
            error_message = getattr(response, "message", "Unknown DashScope error")
            raise AppException(f"DashScope request failed: {error_message}")

        image_payload = self._extract_image_payload(response)
        b64_json = image_payload.get("b64_json")
        image_url = image_payload.get("url")

        if isinstance(b64_json, str) and b64_json:
            return self._convert_base64_to_bytes(b64_json)

        if isinstance(image_url, str) and image_url:
            return self._download_image_bytes(image_url)

        raise AppException("No valid image data found in Qwen response.")

    def _extract_image_payload(self, response: Any) -> dict[str, str]:
        # DashScope SDK responses are object-like; handle both object and dict structures.
        output = getattr(response, "output", None)
        if output is None:
            return {}

        from_choices = self._extract_from_choices(getattr(output, "choices", None))
        if from_choices:
            return from_choices

        return self._extract_from_results(getattr(output, "results", None))

    def _extract_from_choices(self, choices: Any) -> dict[str, str]:
        if not choices:
            return {}

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return {}

        message = first_choice.get("message", {})
        if not isinstance(message, dict):
            return {}

        content = message.get("content", [])
        if not isinstance(content, list):
            return {}

        for item in content:
            payload = self._extract_from_content_item(item)
            if payload:
                return payload

        return {}

    def _extract_from_content_item(self, item: Any) -> dict[str, str]:
        if not isinstance(item, dict):
            return {}

        image_value = item.get("image")
        if isinstance(image_value, str) and image_value:
            return {"url": image_value}

        url_value = item.get("url")
        if isinstance(url_value, str) and url_value:
            return {"url": url_value}

        b64_value = item.get("b64_json")
        if isinstance(b64_value, str) and b64_value:
            return {"b64_json": b64_value}

        return {}

    def _extract_from_results(self, results: Any) -> dict[str, str]:
        if not results:
            return {}

        first = results[0]
        if not isinstance(first, dict):
            return {}

        b64_json = first.get("b64_json")
        if isinstance(b64_json, str) and b64_json:
            return {"b64_json": b64_json}

        url = first.get("url")
        if isinstance(url, str) and url:
            return {"url": url}

        return {}

    def _convert_base64_to_bytes(self, base64_data: str) -> bytes:
        try:
            payload = (
                base64_data.split(",", 1)[1] if "," in base64_data else base64_data
            )
            return base64.b64decode(payload, validate=True)
        except (binascii.Error, ValueError) as e:
            raise AppException(f"Invalid base64 image data from Qwen: {str(e)}")

    def _download_image_bytes(self, image_url: str) -> bytes:
        try:
            request = Request(image_url, headers={"User-Agent": "completeautomate/1.0"})
            with urlopen(request, timeout=30) as response:
                return cast(bytes, response.read())
        except Exception as e:
            raise AppException(f"Failed to download image from Qwen URL: {str(e)}")
