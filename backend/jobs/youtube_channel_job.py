from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import (
    YouTubeChannelCreatorJob,
    YouTubeChannelStatsUpdaterJob,
    YouTubeChannelVideoCheckerJob,
)


class YouTubeChannelJob:
    types = [
        JobTypeEnum.YouTubeChannel,
        JobTypeEnum.YouTubeChannelStatsUpdater,
        JobTypeEnum.YouTubeChannelVideoChecker,
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
        if self.job.type == JobTypeEnum.YouTubeChannelStatsUpdater:
            try:
                status = YouTubeChannelStatsUpdaterJob(self.job).generate()
                return (status, 0)
            except Exception:
                self.job.failed_count += 1
                return (JobsStatusEnum.IN_PROGRESS, self.job.failed_count)
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
        return (JobsStatusEnum.FAILED, 0)
