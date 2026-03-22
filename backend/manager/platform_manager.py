from logging import getLogger

from backend.data import PlatformDBData, PlatformYouTubeChannelDBData
from backend.database import PlatformDB
from backend.enum import PlatformEnum

logger = getLogger(__name__)


class PlatformManager:

    def save_data(self, platform: PlatformDBData) -> str:
        logger.info(f"Saving platform data: {platform.platform_type}")
        try:
            result = PlatformDB().save_data(platform)
            logger.info(f"Platform data saved successfully with ID: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to save platform data: {e}", exc_info=True)
            raise

    def get_platform_by_channel_id(self, channel_id: str) -> str | None:
        logger.info(f"Retrieving platform for channel_id: {channel_id}")
        try:
            ref_id = f"{PlatformEnum.YouTubeChannel.value}#{channel_id}"
            # TODO  Need to fix the return type
            PlatformDB().get_data(ref_id)
            logger.info(f"Platform found for channel_id: {channel_id}")
            return ref_id
        except Exception as e:
            logger.warning(f"Platform not found for channel_id {channel_id}: {e}")
            return None

    def get_platform_by_video_id(self, channel_id: str, video_id: str) -> str | None:
        logger.info(f"Retrieving platform for video_id: {video_id}")
        try:
            ref_id = f"{PlatformEnum.YouTubeVideo.value}#{channel_id}#{video_id}"
            PlatformDB().get_data(ref_id)
            return ref_id
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
