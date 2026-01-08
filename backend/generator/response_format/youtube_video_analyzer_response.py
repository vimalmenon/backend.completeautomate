from typing import List

from pydantic import BaseModel, Field


class YouTubeVideoAnalyzerResponse(BaseModel):

    title: str = Field(description="The title of the YouTube video")
    description: str = Field(description="The description of the YouTube video")
    tags: List[str] = Field(description="A list of tags for the YouTube video")


class YouTubeVideoAnalyzerListResponse(BaseModel):
    videos: List[YouTubeVideoAnalyzerResponse] = Field(
        description="A list of analyzed YouTube videos"
    )
