import logging

from backend.data import (
    JobData,
    YouTubeChannelStatsUpdaterTaskData,
    YouTubeChannelTaskData,
    YouTubeChannelVideoCheckerTaskData,
)
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.manager import JobManager, PlatformManager

logger = logging.getLogger(__name__)


class AddYouTubeChannelServices:

    def add_channel(self, channel_id: str) -> None:
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
        stats_updater_job_data = self.__create_channel_stats_updater_job(
            job_manager=job_manager,
            ref_id=ref_id,
            description=f"Updating stats for YouTube channel with ID: {channel_id}",
        )
        logger.info(
            f"Created stats updater job for YouTube channel with ID: {channel_id}, job: {stats_updater_job_data.to_json()}"
        )

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
            return job_data
        cls_data = YouTubeChannelVideoCheckerTaskData(ref_id=ref_id)
        job_data = job_manager.create_job(
            type=JobTypeEnum.YouTubeChannelVideoChecker,
            task_data=cls_data.to_dict(),
            description=description,
        )
        job_manager.save_job(job_data=job_data)
        return job_data

    def __create_channel_stats_updater_job(
        self, job_manager: JobManager, ref_id: str, description: str
    ) -> JobData:
        if job_data := self.__check_if_job_exists(
            job_manager=job_manager,
            type=JobTypeEnum.YouTubeChannelStatsUpdater,
            ref_id=ref_id,
        ):
            return job_data
        cls_data = YouTubeChannelStatsUpdaterTaskData(ref_id=ref_id)
        job_data = job_manager.create_job(
            type=JobTypeEnum.YouTubeChannelStatsUpdater,
            task_data=cls_data.to_dict(),
            description=description,
            status=JobsStatusEnum.NEW,
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
