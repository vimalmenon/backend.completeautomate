from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import (
    YouTubeChannelCreatorJob,
    YouTubeChannelOnboardingJob,
    YouTubeChannelVideoCheckerJob,
)


class YouTubeChannelJob:
    types = [
        JobTypeEnum.YouTubeChannel,
        JobTypeEnum.YouTubeChannelVideoChecker,
        JobTypeEnum.YouTubeChannelOnboarding,
    ]

    def __init__(self, job: JobData):
        self.job = job

    def execute(self) -> tuple[JobsStatusEnum, int]:
        if self.job.type == JobTypeEnum.YouTubeChannel:
            try:
                status = YouTubeChannelCreatorJob(self.job).generate()
                return (status, 0)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                return (status, 1)
        if self.job.type == JobTypeEnum.YouTubeChannelVideoChecker:
            try:
                status = YouTubeChannelVideoCheckerJob(self.job).generate()
                return (status, 0)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                return (status, 1)
        if self.job.type == JobTypeEnum.YouTubeChannelOnboarding:
            try:
                status = YouTubeChannelOnboardingJob(self.job).generate()
                return (status, 0)
            except Exception:
                self.job.failed_count += 1
                status = (
                    JobsStatusEnum.FAILED
                    if self.job.failed_count >= 4
                    else JobsStatusEnum.IN_PROGRESS
                )
                return (status, 1)
        return (JobsStatusEnum.FAILED, 0)
