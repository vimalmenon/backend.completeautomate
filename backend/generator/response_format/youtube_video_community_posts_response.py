from pydantic import BaseModel, Field


class YouTubeVideoCommunityPostsResponse(BaseModel):
    posts: list[str] = Field(
        description="A list of community posts related to the YouTube video."
    )
