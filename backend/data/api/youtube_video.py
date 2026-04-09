from datetime import datetime

from pydantic import Field

from backend.data.api.base_mode import BaseModelWithConfig


class YouTubeVideoResponse(BaseModelWithConfig):
    ref_id: str
    published_at: datetime
    last_updated_at: datetime
    title: str
    description: str
    thumbnail: str
    tags: list[str]
    language: str
    transcript: str | None = None
    summarized_transcript: str | None = None
    user_message: str | None = None
    community_posts: list[str] = Field(default_factory=list)
    twitter_posts: list[str] = Field(default_factory=list)

    # task_status: YouTubeVideoTaskEnum
    # stats: list[YouTubeVideoDBStats]
    # status: YouTubeVideoStatusEnum = YouTubeVideoStatusEnum.Active
    # metadata_suggestions: list[YouTubeVideoMetadataData] = field(default_factory=list)
    # thumbnail_prompt_suggestions: list[ImagePromptData] = field(default_factory=list)
    # thumbnails_suggestions: list[YouTubeVideoThumbnailData] = field(
    #     default_factory=list
    # )
