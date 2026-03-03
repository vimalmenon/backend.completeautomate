import logging

from backend.data import YouTubeChannelDBData, YouTubeChannelJobData
from backend.database import YouTubeChannelDB
from backend.enum.status import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration.youtube.youtube_api import YouTubeAPI

logger = logging.getLogger(__name__)


class YouTubeChannelGenerator(BaseGenerator):

    def __init__(self, task):
        super().__init__(task)
        self.youtube_api = YouTubeAPI()
        self.job_data = YouTubeChannelJobData.to_cls(self.task.payload)
        self.db = YouTubeChannelDB(self.job_data.platform.channel_id)

    def generate(self) -> TaskStatusEnum:
        channel_from_db = self.db.query_channel()
        if not channel_from_db:
            result = YouTubeAPI().get_channel_info(self.job_data.platform.channel_id)
            channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "task_id": str(self.task.id)}
            )
            self.db.add_channel(channel_from_api)
            logger.info(
                f"Channel with ID {self.job_data.platform.channel_id} added to database for the first time."
            )
        if channel_from_db and channel_from_db.past_update_time(
            int(self.job_data.poll_frequency_in_days)
        ):
            result = YouTubeAPI().get_channel_info(self.job_data.platform.channel_id)
            latest_channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "task_id": str(self.task.id)}
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
