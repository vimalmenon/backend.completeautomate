from datetime import datetime

from backend.data.api.base_mode import BaseModelWithConfig
from backend.data.youtube_channel import (
    YouTubeChannelPlaylistData,
    YouTubeChannelStatsDBData,
)


class ChannelStatsResponse(BaseModelWithConfig):
    subscriber_count: int
    view_count: int
    video_count: int
    timestamp: datetime


class PlaylistResponse(BaseModelWithConfig):
    id: str
    title: str
    description: str
    thumbnail: str


class YouTubeChannelResponse(BaseModelWithConfig):
    ref_id: str
    title: str
    description: str
    custom_url: str
    published_at: datetime
    last_updated_at: datetime
    country: str
    thumbnail_url: str
    banner_image_url: str
    privacy_status: str
    made_for_kids: bool
    stats: list[YouTubeChannelStatsDBData]
    playlist: list[YouTubeChannelPlaylistData]
