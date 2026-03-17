
from pydantic import BaseModel, Field


class YouTubeVideoReviewResponse(BaseModel):
    downsides: list[str] = Field(description="The title of the YouTube video")
    upsides: list[str] = Field(description="The title of the YouTube video")
