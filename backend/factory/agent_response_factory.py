from backend.enum import PromptTaskEnum
from backend.generator.response_format.image_prompt_response import ImagePromptResponse


def agent_response_factory(prompt: PromptTaskEnum, **kwargs):
    return ImagePromptResponse(
        name="cat.jpg",
        prompt="A cute cat sitting on a windowsill, sunlight streaming in, photorealistic",
        description="A photorealistic image of a cat on a windowsill in sunlight",
        negative_prompt="blurry, low quality, watermark",
    )
