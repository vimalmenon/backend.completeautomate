from faker import Faker

from backend.data import (
    PlatformDBData,
    PlatformYouTubeChannelDBData,
    PlatformYouTubeVideoDBData,
)
from backend.enum import PlatformEnum

faker = Faker()


def platform_channel_factory(**kwargs) -> PlatformDBData:

    return PlatformDBData(
        platform_type=PlatformEnum.YouTubeChannel,
        data=PlatformYouTubeChannelDBData(
            channel_id=kwargs.get("channel_id") or str(faker.uuid4())
        ),
    )


def platform_video_factory(**kwargs) -> PlatformDBData:
    return PlatformDBData(
        platform_type=PlatformEnum.YouTubeVideo,
        data=PlatformYouTubeVideoDBData(
            channel_id=kwargs.get("channel_id") or str(faker.uuid4()),
            video_id=kwargs.get("video_id") or str(faker.uuid4()),
        ),
    )
