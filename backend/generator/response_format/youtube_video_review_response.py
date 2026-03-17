from pydantic import BaseModel, Field


class YouTubeVideoReviewResponse(BaseModel):
    downsides: list[str] = Field(
        description="Specific issues or weaknesses in the video, such as pacing, clarity, structure, delivery, or production quality"
    )
    upsides: list[str] = Field(
        description="Specific strengths in the video, such as clarity, engagement, useful insights, storytelling, or production quality"
    )
    overall: str = Field(
        description="A concise overall evaluation summarizing the video's quality, impact, and key improvement focus"
    )
    rating: int = Field(
        description="Overall quality score from 1 to 10, where 10 is excellent and 1 is very poor"
    )
