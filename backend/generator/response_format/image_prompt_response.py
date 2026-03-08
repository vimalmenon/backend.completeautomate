from typing import List

from pydantic import BaseModel, Field


class ImagePromptResponse(BaseModel):
    """Response for an image prompt."""

    name: str = Field(
        description="The name of the image prompt along with file extension"
    )
    prompt: str = Field(description="The generated image prompt")
    description: str = Field(description="A description of the image prompt")
    negative_prompt: str | None = Field(
        default=None, description="The generated negative image prompt"
    )


class ImagePromptsListRequest(BaseModel):
    """Request for a list of image prompts."""

    image_prompts: List[ImagePromptResponse] = Field(
        description="A list of image prompts"
    )
