import base64
import binascii
from typing import Any

from openai import OpenAI

from backend.config.env import env
from backend.exception.app_exception import AppException


class GrokImageGeneration:
    """Grok image generation using xAI's API.

    Grok supports image generation through their API endpoint.
    See: https://docs.x.ai/docs/api-reference/image-generation
    """

    def __init__(self, model: str = "grok-vision-beta"):
        """Initialize Grok image generation.

        Args:
            model: The Grok model to use for image generation.
                   Default is "grok-vision-beta".
        """
        self.model = model
        self.client = self._initialize_client()

    def _initialize_client(self) -> OpenAI:
        """Initialize the OpenAI client for xAI's API."""
        return OpenAI(
            api_key=env.GROK_API_KEY.get_secret_value(),
            base_url="https://api.x.ai/v1",
        )

    def generate(self, prompt: str, size: str = "1024x1024") -> bytes:
        """Generate an image from a text prompt.

        Args:
            prompt: The text description of the image to generate.
            size: The size of the image (e.g., "1024x1024", "512x512").

        Returns:
            The generated image as bytes.

        Raises:
            AppException: If image generation fails.
        """
        try:
            response = self._generate_image(prompt, size)
            return self._parse_response(response)
        except Exception as e:
            raise AppException(f"Grok image generation error: {str(e)}")

    def _generate_image(self, prompt: str, size: str) -> Any:
        """Call Grok API to generate image.

        Args:
            prompt: The text prompt for image generation.
            size: The desired image size.

        Returns:
            API response object.
        """
        response = self.client.images.generate(  # type: ignore[call-overload]
            prompt=prompt,
            model=self.model,
            n=1,
            size=size,
            response_format="b64_json",
        )
        return response

    def _parse_response(self, response: Any) -> bytes:
        """Parse the API response and extract image data.

        Args:
            response: The API response object.

        Returns:
            The image data as bytes.

        Raises:
            AppException: If no image data is found or parsing fails.
        """
        if not response.data:
            raise AppException("No image data found in Grok response.")

        image_data = response.data[0]

        # Handle base64 encoded response
        if hasattr(image_data, "b64_json") and image_data.b64_json:
            return self._convert_base64_to_bytes(image_data.b64_json)

        # Handle URL response (if applicable)
        if hasattr(image_data, "url") and image_data.url:
            raise AppException(
                "URL response format not yet supported. Use b64_json format."
            )

        raise AppException("No valid image data found in response.")

    def _convert_base64_to_bytes(self, base64_data: str) -> bytes:
        """Convert base64 string to bytes.

        Args:
            base64_data: Base64 encoded image string.

        Returns:
            Decoded image bytes.

        Raises:
            AppException: If base64 decoding fails.
        """
        try:
            # Remove data URL prefix if present
            payload = (
                base64_data.split(",", 1)[1] if "," in base64_data else base64_data
            )
            return base64.b64decode(payload, validate=True)
        except (binascii.Error, ValueError) as e:
            raise AppException(f"Invalid base64 image data from Grok: {str(e)}")
