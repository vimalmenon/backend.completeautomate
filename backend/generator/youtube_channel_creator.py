import logging

from backend.data import (
    JobData,
    PlatformDBData,
    PlatformYouTubeChannelDBData,
    PlatformYouTubeVideoDBData,
    YouTubeChannelDBData,
    YouTubeChannelTaskData,
    YouTubeChannelVideoCheckerTaskData,
    YouTubeJobData,
    YouTubeVideoTaskData,
)
from backend.enum import JobsStatusEnum, JobTypeEnum, PlatformEnum, TaskStatusEnum
from backend.generator.base_generator import BaseGenerator, BaseGeneratorJob
from backend.integration.youtube.youtube_api import YouTubeAPI
from backend.manager import (
    JobManager,
    PlatformManager,
    TaskManager,
    YouTubeChannelManager,
    YouTubeVideoManager,
)

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
            return JobsStatusEnum.IN_PROGRESS
        if channel_from_db.past_update_time(int(self.task_data.poll_frequency_in_days)):
            result = YouTubeAPI().get_channel_info(self.task_data.platform.channel_id)
            latest_channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "ref_id": self.task_data.ref_id}
            )
            self.channel_manager.update_channel(
                latest_channel_from_api.values_to_update(channel_from_db)
            )

        return JobsStatusEnum.IN_PROGRESS


class YouTubeChannelVideoCheckerJob(BaseGeneratorJob):

    def __init__(self, job: JobData):
        super().__init__(job)
        self.task_data = YouTubeChannelVideoCheckerTaskData.to_cls(job.task_data)
        self.youtube_api = YouTubeAPI()
        self.channel_manager = YouTubeChannelManager(ref_id=self.task_data.ref_id)
        self.manager = TaskManager()

    def generate(self) -> JobsStatusEnum:
        videos = self.youtube_api.list_all_videos(self.task_data.platform.channel_id)
        for video in videos:
            platform_data = self.__get_platform_data(video["id"])
            video_from_db = YouTubeVideoManager(platform_data.ref_id).get_video()
            if not video_from_db:
                platform_ref_id = self.__create_platform_data(video["id"])

                cls_data = YouTubeVideoTaskData(ref_id=platform_ref_id)
                job_manager = JobManager()
                job_data = job_manager.create_job(
                    type=JobTypeEnum.YouTubeVideo,
                    task_data=cls_data.to_dict(),
                    description=f"Checking video with ID: {video['id']} for YouTube channel with ID: {platform_data.data.channel_id}",
                )
                job_manager.save_job(job_data=job_data)

        return JobsStatusEnum.IN_PROGRESS

    def __get_platform_data(self, video_id: str) -> PlatformDBData:
        return PlatformDBData(
            platform_type=PlatformEnum.YouTubeVideo,
            data=PlatformYouTubeVideoDBData(
                channel_id=self.task_data.platform.channel_id, video_id=video_id
            ),
        )

    def __create_platform_data(self, video_id: str) -> str:
        data = self.__get_platform_data(video_id)
        logger.info(
            "Saving platform data for video id: %s to database with ref_id: %s",
            video_id,
            self.task_data.ref_id,
        )
        return PlatformManager().save_data(data)


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
