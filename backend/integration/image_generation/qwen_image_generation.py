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
        if hasattr(response, "output"):
            output = response.output
            choices = getattr(output, "choices", None)
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", [])
                for item in content:
                    if isinstance(item, dict):
                        if "image" in item and isinstance(item["image"], str):
                            return {"url": item["image"]}
                        if "url" in item and isinstance(item["url"], str):
                            return {"url": item["url"]}
                        if "b64_json" in item and isinstance(item["b64_json"], str):
                            return {"b64_json": item["b64_json"]}

            results = getattr(output, "results", None)
            if results:
                first = results[0]
                if isinstance(first, dict):
                    b64_json = first.get("b64_json")
                    url = first.get("url")
                    if isinstance(b64_json, str):
                        return {"b64_json": b64_json}
                    if isinstance(url, str):
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
