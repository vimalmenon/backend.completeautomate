import logging

from backend.config.env import env
from backend.data import YouTubeChannelDBData, YouTubeJobData
from backend.database import YouTubeChannelDB
from backend.enum import JobEnum, PlatformEnum, TaskStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration.youtube.youtube_api import YouTubeAPI
from backend.manager import TaskManager

logger = logging.getLogger(__name__)


class YouTubeChannelCreator(BaseGenerator):

    def __init__(self, task):
        super().__init__(task)
        self.youtube_api = YouTubeAPI()
        self.job_data = YouTubeJobData.to_cls(self.task.payload)
        self.db = YouTubeChannelDB(self.job_data.platform.channel_id)
        self.manager = TaskManager(task)

    def generate(self) -> TaskStatusEnum:
        channel_from_db = self.db.query_channel()
        if not channel_from_db:
            result = YouTubeAPI().get_channel_info(self.job_data.platform.channel_id)
            channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "task_id": str(self.task.id), "ref_id": self.job_data.ref_id}
            )
            self.db.add_channel(channel_from_api)
            task = self.manager.create_youtube_video_task(
                ref_id=f"{PlatformEnum.YouTubeChannel.value}#{env.YOUTUBE_CHANNEL_ID}",
                created_by=JobEnum.YouTubeChannel,
            )
            self.manager.add_task(task)
            logger.info(
                f"Channel with ID {self.job_data.platform.channel_id} added to database for the first time."
            )
        if channel_from_db and channel_from_db.past_update_time(
            int(self.job_data.poll_frequency_in_days)
        ):
            result = YouTubeAPI().get_channel_info(self.job_data.platform.channel_id)
            latest_channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "task_id": str(self.task.id), "ref_id": self.job_data.ref_id}
            )
            self.db.update_channel(
                latest_channel_from_api.values_to_update(channel_from_db)
            )
            logger.info(
                f"Channel with ID {self.job_data.platform.channel_id} updated in database after polling."
            )
        logger.info(
            f"Channel with ID {self.job_data.platform.channel_id} is up to date in the database. No update needed."
        )
        return TaskStatusEnum.IN_PROGRESS
