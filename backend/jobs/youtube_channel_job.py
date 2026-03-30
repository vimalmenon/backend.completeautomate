import logging

from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import (
    YouTubeChannelCreatorJob,
    YouTubeChannelOnboardingJob,
    YouTubeChannelVideoCheckerJob,
)
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class YouTubeChannelJob(BaseJob):
    types = [
        JobTypeEnum.YouTubeChannelOnboarding,
        JobTypeEnum.YouTubeChannel,
        JobTypeEnum.YouTubeChannelVideoChecker,
    ]

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        if self.job.type == JobTypeEnum.YouTubeChannel:
            try:
                logger.info("Executing YouTube channel job %s", self.job.id)
                status, data = YouTubeChannelCreatorJob(self.job).generate()
                logger.info(
                    "Completed YouTube channel job %s with status %s",
                    self.job.id,
                    status.value,
                )
                return (status, 0, data)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                logger.exception(
                    "YouTube channel job %s failed; retry_status=%s failed_count=%s",
                    self.job.id,
                    status.value,
                    self.job.failed_count,
                )
                return (status, self.job.failed_count, None)
        if self.job.type == JobTypeEnum.YouTubeChannelVideoChecker:
            try:
                logger.info(
                    "Executing YouTube channel video checker job %s", self.job.id
                )
                status, data = YouTubeChannelVideoCheckerJob(self.job).generate()
                logger.info(
                    "Completed YouTube channel video checker job %s with status %s",
                    self.job.id,
                    status.value,
                )
                return (status, 0, data)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                logger.exception(
                    "YouTube channel video checker job %s failed; retry_status=%s failed_count=%s",
                    self.job.id,
                    status.value,
                    self.job.failed_count,
                )
                return (status, self.job.failed_count, None)
        if self.job.type == JobTypeEnum.YouTubeChannelOnboarding:
            try:
                logger.info("Executing YouTube channel onboarding job %s", self.job.id)
                status, data = YouTubeChannelOnboardingJob(self.job).generate()
                logger.info(
                    "Completed YouTube channel onboarding job %s with status %s",
                    self.job.id,
                    status.value,
                )
                return (status, 0, data)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                logger.exception(
                    "YouTube channel onboarding job %s failed; retry_status=%s failed_count=%s",
                    self.job.id,
                    status.value,
                    self.job.failed_count,
                )
                return (status, self.job.failed_count, None)
        logger.warning(
            "Unsupported YouTube channel job type %s for job %s",
            self.job.type.value,
            self.job.id,
        )
        return (JobsStatusEnum.FAILED, 0, None)
