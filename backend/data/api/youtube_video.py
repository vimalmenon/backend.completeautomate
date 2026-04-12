from datetime import datetime

from pydantic import Field

from backend.data.api.base_mode import BaseModelWithConfig
from backend.data.image import ImagePromptData
from backend.data.youtube_video import (
    YouTubeVideoDBStats,
    YouTubeVideoMetadataData,
    YouTubeVideoThumbnailData,
)
from backend.enum import YouTubeVideoStatusEnum, YouTubeVideoTaskEnum


class YouTubeVideoResponse(BaseModelWithConfig):
    ref_id: str
    published_at: datetime
    last_updated_at: datetime
    title: str
    description: str
    thumbnail: str
    task_status: YouTubeVideoTaskEnum
    tags: list[str]
    language: str
    stats: list[YouTubeVideoDBStats]
    transcript: str | None = None
    summarized_transcript: str | None = None
    user_message: str | None = None
    status: YouTubeVideoStatusEnum = YouTubeVideoStatusEnum.Active
    metadata_suggestions: list[YouTubeVideoMetadataData] = Field(default_factory=list)
    thumbnail_prompt_suggestions: list[ImagePromptData] = Field(default_factory=list)
    thumbnails_suggestions: list[YouTubeVideoThumbnailData] = Field(default_factory=list)
    community_posts: list[str] = Field(default_factory=list)
    twitter_posts: list[str] = Field(default_factory=list)
