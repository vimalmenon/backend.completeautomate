import logging

from backend.data import YouTubeChannelTaskData
from backend.enum import JobTypeEnum
from backend.manager import JobManager, PlatformManager

logger = logging.getLogger(__name__)


class AddYouTubeChannelServices:

    def add_channel(self, channel_id: str) -> str:
        ref_id = self.__create_channel_platform_if_not_exists(channel_id)
        cls_data = YouTubeChannelTaskData(ref_id=ref_id)
        data = JobManager().create_job(
            type=JobTypeEnum.YouTubeChannel,
            task_data=cls_data.to_dict(),
            description=f"Processing YouTube channel with ID: {channel_id}",
        )
        logger.info(
            f"Created job for YouTube channel with ID: {channel_id}, job ID: {data.id}"
        )
        JobManager().save_job(job_data=data)

    def __create_channel_platform_if_not_exists(self, channel_id: str) -> str:
        if ref_id := PlatformManager().get_platform_by_channel_id(channel_id):
            logger.info(
                f"Platform already exists for channel_id: {channel_id}, ref_id: {ref_id}"
            )
            return ref_id
        else:
            channel_data = PlatformManager().create_channel_data(channel_id)
            logger.info(f"Creating new platform for channel_id: {channel_id}")
            return PlatformManager().save_data(channel_data)
