import logging

from backend.config.env import env
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
from backend.integration.youtube.mock_youtube_api import MockYouTubeAPI
from backend.integration.youtube.youtube_api import YouTubeAPI
from backend.manager import (
    JobManager,
    PlatformManager,
    TaskManager,
    YouTubeChannelManager,
    YouTubeVideoManager,
)

logger = logging.getLogger(__name__)


class YouTubeChannelOnboardingJob(BaseGeneratorJob):
    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
        channel_id = env.YOUTUBE_CHANNEL_ID
        ref_id = self.__create_channel_platform_if_not_exists(channel_id=channel_id)
        job_manager = JobManager()
        job_data = self.__create_channel_job(
            job_manager=job_manager,
            ref_id=ref_id,
            description=f"Processing YouTube channel with ID: {channel_id}",
        )
        logger.info(
            f"Created job for YouTube channel with ID: {channel_id}, job: {job_data.to_json()}"
        )
        video_checker_job_data = self.__create_channel_video_checker_job(
            job_manager=job_manager,
            ref_id=ref_id,
            description=f"Checking videos for YouTube channel with ID: {channel_id}",
        )
        logger.info(
            f"Created video checker job for YouTube channel with ID: {channel_id}, job: {video_checker_job_data.to_json()}"
        )
        return JobsStatusEnum.IN_PROGRESS, None

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

    def __create_channel_job(
        self, job_manager: JobManager, ref_id: str, description: str
    ) -> JobData:
        if job_data := self.__check_if_job_exists(
            job_manager=job_manager, type=JobTypeEnum.YouTubeChannel, ref_id=ref_id
        ):
            logger.info(
                f"Job already exists for YouTube channel with ref_id: {ref_id}, "
                f"job: {job_data.to_json()}"
            )
            return job_data
        cls_data = YouTubeChannelTaskData(ref_id=ref_id)
        job_data = job_manager.create_job(
            type=JobTypeEnum.YouTubeChannel,
            task_data=cls_data.to_dict(),
            description=description,
        )
        job_manager.save_job(job_data=job_data)
        return job_data

    def __create_channel_video_checker_job(
        self, job_manager: JobManager, ref_id: str, description: str
    ) -> JobData:
        if job_data := self.__check_if_job_exists(
            job_manager=job_manager,
            type=JobTypeEnum.YouTubeChannelVideoChecker,
            ref_id=ref_id,
        ):
            logger.info(
                f"Job already exists for YouTube channel video checker with ref_id: {ref_id}, "
                f"job: {job_data.to_json()}"
            )
            return job_data
        cls_data = YouTubeChannelVideoCheckerTaskData(ref_id=ref_id)
        job_data = job_manager.create_job(
            type=JobTypeEnum.YouTubeChannelVideoChecker,
            task_data=cls_data.to_dict(),
            description=description,
        )
        job_manager.save_job(job_data=job_data)
        return job_data

    def __check_if_job_exists(
        self, job_manager: JobManager, type: JobTypeEnum, ref_id: str
    ) -> JobData | None:
        jobs = job_manager.get_job_by_type(type=type)
        jobs_with_ref_id = [
            job for job in jobs if job.task_data.get("ref_id") == ref_id
        ]
        return jobs_with_ref_id[0] if len(jobs_with_ref_id) > 0 else None


class YouTubeChannelCreatorJob(BaseGeneratorJob):

    def __init__(self, job: JobData):
        super().__init__(job)
        self.task_data = YouTubeChannelTaskData.to_cls(job.task_data)
        self.youtube_api: YouTubeAPI | MockYouTubeAPI = (
            MockYouTubeAPI() if env.OFFLINE else YouTubeAPI()
        )
        self.channel_manager = YouTubeChannelManager(ref_id=self.task_data.ref_id)

    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
        channel_from_db = self.channel_manager.get_channel_details()
        if not channel_from_db:
            result = self.youtube_api.get_channel_info(self.task_data.platform.channel_id)
            channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "ref_id": self.task_data.ref_id}
            )
            self.channel_manager.add_channel(channel_from_api)
            return JobsStatusEnum.IN_PROGRESS, None
        if channel_from_db.past_update_time(int(self.task_data.poll_frequency_in_days)):
            result = self.youtube_api.get_channel_info(self.task_data.platform.channel_id)
            latest_channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "ref_id": self.task_data.ref_id}
            )
            self.channel_manager.update_channel(
                latest_channel_from_api.values_to_update(channel_from_db)
            )

        return JobsStatusEnum.IN_PROGRESS, None


class YouTubeChannelVideoCheckerJob(BaseGeneratorJob):

    def __init__(self, job: JobData):
        super().__init__(job)
        self.task_data = YouTubeChannelVideoCheckerTaskData.to_cls(job.task_data)
        self.youtube_api: YouTubeAPI | MockYouTubeAPI = (
            MockYouTubeAPI() if env.OFFLINE else YouTubeAPI()
        )
        self.channel_manager = YouTubeChannelManager(ref_id=self.task_data.ref_id)
        self.manager = TaskManager()

    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
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
                    task_data=cls_data.to_json(),
                    description=f"Checking video with ID: {video['id']} for YouTube channel with ID: {platform_data.data.channel_id}",
                )
                job_manager.save_job(job_data=job_data)

        return JobsStatusEnum.IN_PROGRESS, None

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
        self.youtube_api: YouTubeAPI | MockYouTubeAPI = (
            MockYouTubeAPI() if env.OFFLINE else YouTubeAPI()
        )
        self.job_data = YouTubeJobData.to_cls(self.task.payload)
        self.manager = TaskManager(task)
        self.channel_manager = YouTubeChannelManager(ref_id=self.job_data.ref_id)

    def generate(self) -> TaskStatusEnum:
        channel_from_db = self.channel_manager.get_channel_details()
        if not channel_from_db:
            result = self.youtube_api.get_channel_info(self.job_data.platform.channel_id)
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
            result = self.youtube_api.get_channel_info(self.job_data.platform.channel_id)
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
