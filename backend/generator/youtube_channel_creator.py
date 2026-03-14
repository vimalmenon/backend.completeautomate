import logging

from backend.data import (
    JobData,
    PlatformDBData,
    PlatformYouTubeChannelDBData,
    YouTubeChannelDBData,
    YouTubeChannelTaskData,
    YouTubeJobData,
)
from backend.enum import JobsStatusEnum, PlatformEnum, TaskStatusEnum
from backend.generator.base_generator import BaseGenerator, BaseGeneratorJob
from backend.integration.youtube.youtube_api import YouTubeAPI
from backend.manager import TaskManager, YouTubeChannelManager

logger = logging.getLogger(__name__)


class YouTubeChannelCreatorJob(BaseGeneratorJob):

    def __init__(self, job: JobData):
        super().__init__(job)
        self.task_data = YouTubeChannelTaskData.to_cls(job.task_data)

        self.youtube_api = YouTubeAPI()
        self.channel_manager = YouTubeChannelManager(ref_id=self.task_data.ref_id)

    def generate(self) -> JobsStatusEnum:
        channel_from_db = self.channel_manager.get_channel_details()
        if not channel_from_db:
            result = YouTubeAPI().get_channel_info(self.task_data.platform.channel_id)
            channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "ref_id": self.task_data.ref_id}
            )
            self.channel_manager.add_channel(channel_from_api)
        return JobsStatusEnum.COMPLETE


class YouTubeChannelCreator(BaseGenerator):

    def __init__(self, task):
        super().__init__(task)
        self.youtube_api = YouTubeAPI()
        self.job_data = YouTubeJobData.to_cls(self.task.payload)
        self.manager = TaskManager(task)
        self.channel_manager = YouTubeChannelManager(ref_id=self.job_data.ref_id)

    def generate(self) -> TaskStatusEnum:
        channel_from_db = self.channel_manager.get_channel_details()
        if not channel_from_db:
            result = YouTubeAPI().get_channel_info(self.job_data.platform.channel_id)
            channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "task_id": str(self.task.id), "ref_id": self.job_data.ref_id}
            )
            self.channel_manager.add_channel(channel_from_api)
            platform_data = self.__get_platform_data()
            task = self.manager.create_youtube_video_task(
                ref_id=platform_data.ref_id,
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
            self.channel_manager.update_channel(
                latest_channel_from_api.values_to_update(channel_from_db)
            )
            logger.info(
                f"Channel with ID {self.job_data.platform.channel_id} updated in database after polling."
            )
        logger.info(
            f"Channel with ID {self.job_data.platform.channel_id} is up to date in the database. No update needed."
        )
        return TaskStatusEnum.IN_PROGRESS

    def __get_platform_data(self) -> PlatformDBData:
        return PlatformDBData(
            platform_type=PlatformEnum.YouTubeChannel,
            data=PlatformYouTubeChannelDBData(
                channel_id=self.job_data.platform.channel_id
            ),
        )
