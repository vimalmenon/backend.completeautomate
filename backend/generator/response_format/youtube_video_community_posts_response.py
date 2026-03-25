from typing import Any

from pydantic import BaseModel, Field


class YouTubeVideoCommunityPostsResponse(BaseModel):
    posts: list[Any] = Field(description="Provides a list of community post")
