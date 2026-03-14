from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import YouTubeChannelCreatorJob, YouTubeChannelStatsUpdaterJob


class YouTubeChannelJob:
    types = [JobTypeEnum.YouTubeChannel, JobTypeEnum.YouTubeChannelStatsUpdater]

    def __init__(self, job: JobData):
        self.job = job

    def execute(self) -> tuple[JobsStatusEnum, int]:
        if self.job.type == JobTypeEnum.YouTubeChannel:
            try:
                status = YouTubeChannelCreatorJob(self.job).generate()
                return (status, 0)
            except Exception:
                self.job.failed_count += 1
                if self.job.failed_count >= 4:
                    return (JobsStatusEnum.FAILED, 1)
                return (JobsStatusEnum.IN_PROGRESS, self.job.failed_count)
        if self.job.type == JobTypeEnum.YouTubeChannelStatsUpdater:
            try:
                status = YouTubeChannelStatsUpdaterJob(self.job).generate()
                return (status, 0)
            except Exception:
                self.job.failed_count += 1
                return (JobsStatusEnum.IN_PROGRESS, self.job.failed_count)
        return (JobsStatusEnum.FAILED, 0)
