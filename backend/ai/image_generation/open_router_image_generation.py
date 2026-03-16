import base64
import binascii
from enum import Enum
from typing import Any, cast

from openai import OpenAI

from backend.config.env import env
from backend.exception.app_exception import AppException


class ImageModelList(Enum):
    GEMINI_THREE_PRO_IMAGE = "google/gemini-3-pro-image-preview"
    FLUX = "black-forest-labs/flux.2-flex"


class OpenRouterImageGeneration:
    def __init__(self, model: ImageModelList = ImageModelList.FLUX):
        self.model = model

    def __initialize_model(self):
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=env.OPEN_ROUTE_API_KEY.get_secret_value(),
        )

    def generate(self, prompt: str) -> bytes:
        try:
            response = self.__generate_image(prompt)
            return self.__parse_response(response)
        except Exception as e:
            raise AppException(f"Error generating image: {str(e)}")

    # Private method
    def __generate_image(self, prompt: str) -> Any:
        client = self.__initialize_model()

        # Other models use chat completion with image modality
        return client.chat.completions.create(
            model=self.model.value,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            extra_body={"modalities": ["image"]},
        )

    def __parse_response(self, response) -> bytes:
        # Handle OpenRouter chat completion response
        response = response.choices[0].message
        if response.images:
            for image in response.images:
                return self.__convert_base64_to_bytes(image["image_url"]["url"])
        raise AppException("No image found in the response.")

    def __convert_base64_to_bytes(self, base64_data: str) -> bytes:
        try:
            payload = (
                base64_data.split(",", 1)[1] if "," in base64_data else base64_data
            )
            return base64.b64decode(payload, validate=True)
        except (binascii.Error, ValueError) as e:
            raise AppException(f"Invalid base64 image data: {str(e)}")

    def __download_image_bytes(self, image_url: str) -> bytes:
        from urllib.request import Request, urlopen

        try:
            request = Request(image_url, headers={"User-Agent": "completeautomate/1.0"})
            with urlopen(request, timeout=30) as response:
                return cast(bytes, response.read())
        except Exception as e:
            raise AppException(f"Failed to download image URL data: {str(e)}")
