from typing import List

from pydantic import BaseModel, Field


class ImagePromptResponse(BaseModel):
    """Response for an image prompt."""

    name: str = Field(
        description="A short, descriptive output filename for the image prompt result, including file extension"
    )
    prompt: str = Field(
        description="A detailed positive prompt describing subject, style, composition, lighting, and quality cues"
    )
    description: str = Field(
        description="A concise human-readable summary of what the generated image should depict"
    )
    negative_prompt: str | None = Field(
        default=None,
        description="Optional negative prompt listing unwanted elements, artifacts, or styles to avoid",
    )


class ImagePromptsListRequest(BaseModel):
    """Request for a list of image prompts."""

    image_prompts: List[ImagePromptResponse] = Field(
        description="A list of generated image prompt entries, each containing filename, prompt, summary, and optional negative prompt"
    )
