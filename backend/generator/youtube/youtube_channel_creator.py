import logging

from backend.config.env import env
from backend.data import (
    JobData,
    PlatformDBData,
    PlatformYouTubeVideoDBData,
    YouTubeChannelDBData,
    YouTubeChannelTaskData,
    YouTubeChannelVideoCheckerTaskData,
    YouTubeVideoTaskData,
)
from backend.enum import JobsStatusEnum, JobTypeEnum, PlatformEnum
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.integration.youtube.mock_youtube_api import MockYouTubeAPI
from backend.integration.youtube.youtube_api import YouTubeAPI
from backend.manager import (
    JobManager,
    PlatformManager,
    YouTubeChannelManager,
)

logger = logging.getLogger(__name__)


class YouTubeChannelOnboardingJob(BaseGenerator):
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
        if platform := PlatformManager().get_platform_by_channel_id(channel_id):
            logger.info(
                f"Platform already exists for channel_id: {channel_id}, ref_id: {platform.ref_id}"
            )
            return platform.ref_id
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


class YouTubeChannelCreatorJob(BaseGenerator):

    def __init__(self, job: JobData):
        super().__init__(job)
        self.task_data = YouTubeChannelTaskData.to_cls(job.task_data)
        self.youtube_api: YouTubeAPI | MockYouTubeAPI = (
            MockYouTubeAPI() if env.OFFLINE else YouTubeAPI()
        )
        self.channel_manager = YouTubeChannelManager(ref_id=self.task_data.ref_id)
        self.channel_id = self.task_data.platform.channel_id

    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
        channel_from_db = self.channel_manager.get_channel_details()
        if not channel_from_db:
            result = self.youtube_api.get_channel_info(channel_id=self.channel_id)
            channel_from_api = YouTubeChannelDBData.to_cls_from_response(
                {**result, "ref_id": self.task_data.ref_id}
            )
            self.channel_manager.add_channel(channel_from_api)
            return JobsStatusEnum.COMPLETE, None
        # TODO Need to check why this is failing
        raise AppException("Channel DB already exists")


class YouTubeChannelVideoCheckerJob(BaseGenerator):

    def __init__(self, job: JobData):
        super().__init__(job)
        self.task_data = YouTubeChannelVideoCheckerTaskData.to_cls(job.task_data)
        self.youtube_api: YouTubeAPI | MockYouTubeAPI = (
            MockYouTubeAPI() if env.OFFLINE else YouTubeAPI()
        )
        self.channel_manager = YouTubeChannelManager(ref_id=self.task_data.ref_id)

    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
        videos = self.youtube_api.list_all_videos(self.task_data.platform.channel_id)
        for video in videos:
            platform_data = self.__get_platform_data(video["id"])
            platform = PlatformManager().get_platform_by_ref_id(
                ref_id=platform_data.ref_id
            )
            if not platform:
                platform_ref_id = self.__create_platform_data(platform_data)

                cls_data = YouTubeVideoTaskData(ref_id=platform_ref_id)
                job_manager = JobManager()
                job_data = job_manager.create_job(
                    type=JobTypeEnum.YouTubeVideo,
                    task_data=cls_data.to_json(),
                    description=f"Checking video with ID: {video['id']} for YouTube channel with ID: {platform_data.channel_id}",
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

    def __create_platform_data(self, data: PlatformDBData) -> str:
        return PlatformManager().save_data(data)
