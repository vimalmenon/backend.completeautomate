from backend.data import PlatformDBData, PlatformYouTubeChannelDBData
from backend.database import PlatformDB
from backend.enum import PlatformEnum


class PlatformManager:

    def save_data(self, platform: PlatformDBData) -> str:
        return PlatformDB().save_data(platform)

    def get_platform_by_channel_id(self, channel_id: str) -> str | None:
        try:
            ref_id = f"{PlatformEnum.YouTubeChannel.value}#{channel_id}"
            PlatformDB().get_data(ref_id)
            return ref_id
        except Exception:
            return None

    def create_channel_data(self, channel_id: str) -> PlatformDBData:
        return PlatformDBData(
            platform_type=PlatformEnum.YouTubeVideo,
            data=PlatformYouTubeChannelDBData(channel_id=channel_id),
        )
