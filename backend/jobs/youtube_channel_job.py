from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import (
    YouTubeChannelCreatorJob,
    YouTubeChannelOnboardingJob,
    YouTubeChannelVideoCheckerJob,
)
from backend.jobs.base_job import BaseNewJob


class YouTubeChannelJob(BaseNewJob):
    types = [
        JobTypeEnum.YouTubeChannelOnboarding,
        JobTypeEnum.YouTubeChannel,
        JobTypeEnum.YouTubeChannelVideoChecker,
    ]

    def __init__(self, job: JobData):
        self.job = job

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        if self.job.type == JobTypeEnum.YouTubeChannel:
            try:
                status = YouTubeChannelCreatorJob(self.job).generate()
                return (status, 0, None)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                return (status, 1, None)
        if self.job.type == JobTypeEnum.YouTubeChannelVideoChecker:
            try:
                status = YouTubeChannelVideoCheckerJob(self.job).generate()
                return (status, 0, None)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                return (status, 1, None)
        if self.job.type == JobTypeEnum.YouTubeChannelOnboarding:
            try:
                status = YouTubeChannelOnboardingJob(self.job).generate()
                return (status, 0, None)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                return (status, 1, None)
        return (JobsStatusEnum.FAILED, 0, None)
