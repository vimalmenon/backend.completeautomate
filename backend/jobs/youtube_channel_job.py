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
        logger.info("Executing YouTube channel job %s", self.job.id)
        try:
            if self.job.type == JobTypeEnum.YouTubeChannel:
                status, data = YouTubeChannelCreatorJob(self.job).generate()
                logger.info(
                    "Completed YouTube channel job %s with status %s",
                    self.job.id,
                    status.value,
                )
                return (status, 0, data)
            elif self.job.type == JobTypeEnum.YouTubeChannelVideoChecker:
                status, data = YouTubeChannelVideoCheckerJob(self.job).generate()
                logger.info(
                    "Completed YouTube channel video checker job %s with status %s",
                    self.job.id,
                    status.value,
                )
                return (status, 0, data)
            elif self.job.type == JobTypeEnum.YouTubeChannelOnboarding:
                status, data = YouTubeChannelOnboardingJob(self.job).generate()
                logger.info(
                    "Completed YouTube channel onboarding job %s with status %s",
                    self.job.id,
                    status.value,
                )
                return (status, 0, data)
            self.job.failed_count += 1
            status = (
                JobsStatusEnum.FAILED
                if self.job.failed_count >= 4
                else JobsStatusEnum.IN_PROGRESS
            )
            return (status, self.job.failed_count, None)
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
