from backend.data import (
    PlatformDBData,
    PlatformYouTubeChannelDBData,
    PlatformYouTubeVideoDBData,
)
from backend.enum import PlatformEnum


def platform_channel_factory(**kwargs) -> PlatformDBData:

    return PlatformDBData(
        platform_type=PlatformEnum.YouTubeChannel,
        data=PlatformYouTubeChannelDBData(channel_id=kwargs.get("channel_id")),
    )


def platform_video_factory(**kwargs) -> PlatformDBData:
    return PlatformDBData(
        platform_type=PlatformEnum.YouTubeVideo,
        data=PlatformYouTubeVideoDBData(
            channel_id=kwargs.get("channel_id"), video_id=kwargs.get("video_id")
        ),
    )
