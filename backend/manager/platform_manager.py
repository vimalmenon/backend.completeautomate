from logging import getLogger

from backend.data import PlatformDBData, PlatformYouTubeChannelDBData
from backend.database import PlatformDB
from backend.enum import PlatformEnum

logger = getLogger(__name__)


class PlatformManager:

    def get_all_platforms(self) -> list[PlatformDBData]:
        logger.info("Retrieving all platforms")
        try:
            platforms = PlatformDB().get_platforms()
            logger.info(f"Retrieved {len(platforms)} platforms")
            return platforms
        except Exception as e:
            logger.error(f"Failed to retrieve platforms: {e}", exc_info=True)
            raise

    def save_data(self, platform: PlatformDBData) -> str:
        logger.info(f"Saving platform data: {platform.platform_type}")
        try:
            result = PlatformDB().save_data(platform)
            logger.info(f"Platform data saved successfully with ID: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to save platform data: {e}", exc_info=True)
            raise

    def get_platform_by_ref_id(self, ref_id: str) -> PlatformDBData | None:
        logger.info(f"Retrieving platform for ref_id: {ref_id}")
        try:
            platform = PlatformDB().get_data(ref_id)
            logger.info(f"Platform found for ref_id: {ref_id}")
            return platform
        except Exception as e:
            logger.warning(f"Platform not found for ref_id {ref_id}: {e}")
            return None

    def get_platform_by_channel_id(self, channel_id: str) -> PlatformDBData | None:
        logger.info(f"Retrieving platform for channel_id: {channel_id}")
        try:
            ref_id = f"{PlatformEnum.YouTubeChannel.value}#{channel_id}"
            platform = PlatformDB().get_data(ref_id)
            logger.info(f"Platform found for channel_id: {channel_id}")
            return platform
        except Exception as e:
            logger.warning(f"Platform not found for channel_id {channel_id}: {e}")
            return None

    def get_platform_by_video_id(
        self, channel_id: str, video_id: str
    ) -> PlatformDBData | None:
        logger.info(f"Retrieving platform for video_id: {video_id}")
        try:
            ref_id = f"{PlatformEnum.YouTubeVideo.value}#{channel_id}#{video_id}"
            return PlatformDB().get_data(ref_id)
        except Exception as e:
            logger.warning(f"Platform not found for video_id {video_id}: {e}")
            return None

    def create_channel_data(self, channel_id: str) -> PlatformDBData:
        logger.debug(f"Creating channel data for channel_id: {channel_id}")
        platform_data = PlatformDBData(
            platform_type=PlatformEnum.YouTubeChannel,
            data=PlatformYouTubeChannelDBData(channel_id=channel_id),
        )
        logger.debug(f"Channel data created for channel_id: {channel_id}")
        return platform_data
