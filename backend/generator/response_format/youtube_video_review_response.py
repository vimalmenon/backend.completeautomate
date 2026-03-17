from pydantic import BaseModel, Field


class YouTubeVideoReviewResponse(BaseModel):
    downsides: list[str] = Field(description="List out all the downsides of Video")
    upsides: list[str] = Field(description="List out all the positive sides")
    overall: str = Field(description="Overall Video comment")
    rating: int = Field(description="Rate  this video out of 10")
